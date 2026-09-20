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
