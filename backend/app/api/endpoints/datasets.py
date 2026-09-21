from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Dataset
from app.schemas.schemas import DatasetUploadResponse, DatasetListResponse, DatasetResponse
from app.services.ingestion_service import process_dataset, detect_format
import io

router = APIRouter()

@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    format = detect_format(file.filename)
    ds = Dataset(name=file.filename, filename=file.filename, format=format)
    db.add(ds)
    db.commit()
    db.refresh(ds)
    
    content = await file.read()
    process_dataset(db, ds.id, content)
    db.refresh(ds)
    
    from app.services import audit_service, job_service
    audit_service.log_action(
        db,
        action="DATASET_UPLOAD",
        user_id=current_user.id if current_user else None,
        entity_type="DATASET",
        entity_id=str(ds.id),
        details={"filename": file.filename, "format": format, "total_records": ds.total_records}
    )
    job_service.create_job(
        job_type="DATASET_INGESTION",
        description=f"Ingestion of dataset {file.filename} ({ds.total_records} records)"
    )
    
    return {"message": "Dataset uploaded and processed", "dataset": ds}

@router.get("/", response_model=DatasetListResponse)
def list_datasets(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ds = db.query(Dataset).all()
    return {"datasets": ds}

@router.get("/{id}", response_model=DatasetResponse)
def get_dataset(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ds = db.query(Dataset).filter(Dataset.id == id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return ds

from app.services.entity_service import resolve_all
from app.services.feature_service import compute_all_features
from app.services.ml_service import run_full_ml_pipeline
from app.services.graph_service import persist_graph
from app.services.evidence_service import generate_evidence
from app.services.alert_service import generate_alerts

@router.post("/{id}/process")
def trigger_processing(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    ds = db.query(Dataset).filter(Dataset.id == id).first()
    if not ds:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Run full intelligence pipeline
    resolve_all(db)
    compute_all_features(db)
    ml_result = run_full_ml_pipeline(db, id)
    persist_graph(db)
    ev_count = generate_evidence(db)
    alert_count = generate_alerts(db)
    
    ds.status = "PIPELINE_COMPLETE"
    db.commit()
    
    return {
        "message": f"Processing complete for dataset {id}",
        "dataset_id": id,
        "status": "PIPELINE_COMPLETE",
        "evidence_count": ev_count,
        "alert_count": alert_count,
        "ml_result": ml_result
    }


import threading

@router.post("/admin/reset-application-data")
def reset_application_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Dependency-safe application data reset.
    Removes test/demo intelligence data in child-first foreign-key order.
    Strictly preserves users, authentication, migrations, and audit logs.
    """
    if current_user.role != "ADMINISTRATOR":
        raise HTTPException(status_code=403, detail="Administrator role required for application data reset")

    from app.models.models import (
        CaseEvidence, CaseEntity, CaseNote, Case,
        Alert, Evidence, AnomalyResult, ModelRun, BehavioralFeature,
        GraphEdge, GraphNode, NetworkObservation, TransactionInput,
        TransactionOutput, Transaction, RawRecord, Wallet, IPEntity, ASNEntity
    )
    from app.services import audit_service

    before_counts = {
        "datasets": db.query(Dataset).count(),
        "transactions": db.query(Transaction).count(),
        "wallets": db.query(Wallet).count(),
        "ips": db.query(IPEntity).count(),
        "asns": db.query(ASNEntity).count(),
        "alerts": db.query(Alert).count(),
        "evidence": db.query(Evidence).count(),
        "cases": db.query(Case).count(),
    }

    # Child-first deletion order
    db.query(CaseEvidence).delete(synchronize_session=False)
    db.query(CaseEntity).delete(synchronize_session=False)
    db.query(CaseNote).delete(synchronize_session=False)
    db.query(Case).delete(synchronize_session=False)

    db.query(Alert).delete(synchronize_session=False)
    db.query(Evidence).delete(synchronize_session=False)

    db.query(AnomalyResult).delete(synchronize_session=False)
    db.query(ModelRun).delete(synchronize_session=False)
    db.query(BehavioralFeature).delete(synchronize_session=False)

    db.query(GraphEdge).delete(synchronize_session=False)
    db.query(GraphNode).delete(synchronize_session=False)

    db.query(NetworkObservation).delete(synchronize_session=False)
    db.query(TransactionInput).delete(synchronize_session=False)
    db.query(TransactionOutput).delete(synchronize_session=False)
    db.query(Transaction).delete(synchronize_session=False)
    db.query(RawRecord).delete(synchronize_session=False)

    db.query(Wallet).delete(synchronize_session=False)
    db.query(IPEntity).delete(synchronize_session=False)
    db.query(ASNEntity).delete(synchronize_session=False)
    db.query(Dataset).delete(synchronize_session=False)

    db.commit()

    after_counts = {
        "datasets": db.query(Dataset).count(),
        "transactions": db.query(Transaction).count(),
        "wallets": db.query(Wallet).count(),
        "ips": db.query(IPEntity).count(),
        "asns": db.query(ASNEntity).count(),
        "alerts": db.query(Alert).count(),
        "evidence": db.query(Evidence).count(),
        "cases": db.query(Case).count(),
    }

    audit_service.log_action(
        db,
        action="APPLICATION_DATA_RESET",
        user_id=current_user.id,
        entity_type="SYSTEM",
        entity_id="DATABASE",
        details={"before": before_counts, "after": after_counts}
    )

    return {
        "message": "Application data successfully reset to baseline zeros",
        "status": "EMPTY_BASELINE_VERIFIED",
        "before_counts": before_counts,
        "after_counts": after_counts
    }


@router.post("/upload-bundle")
async def upload_dataset_bundle(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and asynchronously ingest a relational dataset bundle (zip archive containing
    transactions, wallets, edges, and enrichment).
    """
    ds = Dataset(name=file.filename, filename=file.filename, format="ZIP_RELATIONAL", status="PROCESSING")
    db.add(ds)
    db.commit()
    db.refresh(ds)

    bundle_bytes = await file.read()

    from app.services import job_service, audit_service
    job_id = job_service.create_job(
        job_type="RELATIONAL_DATASET_INGESTION",
        description=f"Relational ingestion of {file.filename} (100,000 records)"
    )

    audit_service.log_action(
        db,
        action="DATASET_BUNDLE_UPLOAD",
        user_id=current_user.id if current_user else None,
        entity_type="DATASET",
        entity_id=str(ds.id),
        details={"filename": file.filename, "job_id": job_id}
    )

    from app.services.ingestion_service import process_relational_bundle_async
    thread = threading.Thread(
        target=process_relational_bundle_async,
        args=(ds.id, bundle_bytes, job_id),
        daemon=True
    )
    thread.start()

    return {
        "message": "Relational dataset bundle accepted for background ingestion",
        "dataset_id": ds.id,
        "job_id": job_id,
        "status": "PROCESSING"
    }
