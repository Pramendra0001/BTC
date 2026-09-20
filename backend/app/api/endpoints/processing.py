from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Dataset
from app.services.entity_service import resolve_all
from app.services.feature_service import compute_all_features
from app.services.ml_service import run_full_ml_pipeline
from app.services.graph_service import persist_graph
from app.services.evidence_service import generate_evidence
from app.services.alert_service import generate_alerts
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/run-pipeline")
def trigger_pipeline(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run the complete intelligence pipeline on a dataset:
    Entity Resolution → Feature Engineering → ML → Graph → Evidence → Alerts
    """
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    if ds.status not in ("COMPLETED", "PROCESSING_PIPELINE"):
        raise HTTPException(
            status_code=400,
            detail=f"Dataset must be in COMPLETED state to run pipeline (current: {ds.status})"
        )

    ds.status = "PROCESSING_PIPELINE"
    db.commit()

    try:
        logger.info(f"Starting pipeline for dataset {dataset_id}")

        # Step 1: Entity resolution
        logger.info("Step 1: Entity resolution...")
        resolve_all(db)

        # Step 2: Feature engineering
        logger.info("Step 2: Feature engineering...")
        compute_all_features(db)

        # Step 3: ML (Isolation Forest + DBSCAN)
        logger.info("Step 3: ML anomaly detection & clustering...")
        ml_result = run_full_ml_pipeline(db, dataset_id)

        # Step 4: Graph construction & persistence
        logger.info("Step 4: Graph construction...")
        persist_graph(db)

        # Step 5: Evidence generation
        logger.info("Step 5: Evidence generation...")
        evidence_count = generate_evidence(db)

        # Step 6: Alert prioritization
        logger.info("Step 6: Alert generation...")
        alert_count = generate_alerts(db)

        ds.status = "PIPELINE_COMPLETE"
        db.commit()

        return {
            "message": "Pipeline completed successfully",
            "dataset_id": dataset_id,
            "status": "PIPELINE_COMPLETE",
            "results": {
                "ml": ml_result,
                "evidence_count": evidence_count,
                "alert_count": alert_count,
            }
        }

    except Exception as e:
        logger.error(f"Pipeline failed for dataset {dataset_id}: {e}")
        ds.status = "PIPELINE_FAILED"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")


@router.get("/status/{dataset_id}")
def pipeline_status(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ds = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return {
        "dataset_id": dataset_id,
        "status": ds.status,
        "total_records": ds.total_records,
        "valid_records": ds.valid_records,
        "invalid_records": ds.invalid_records,
    }
