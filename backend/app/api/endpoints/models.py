from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, ModelRun
from app.schemas.schemas import ModelRunResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[ModelRunResponse])
def list_models(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ModelRun).offset(skip).limit(limit).all()

@router.get("/{id}", response_model=ModelRunResponse)
def get_model(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    m = db.query(ModelRun).filter(ModelRun.id == id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Model run not found")
    return m
