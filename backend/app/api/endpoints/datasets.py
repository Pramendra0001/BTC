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

@router.post("/{id}/process")
def trigger_processing(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Triggering reprocessing is a placeholder here
    return {"message": f"Processing triggered for dataset {id}"}
