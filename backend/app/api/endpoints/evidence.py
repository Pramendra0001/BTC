from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Evidence
from app.schemas.schemas import EvidenceResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[EvidenceResponse])
def list_evidence(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Evidence).offset(skip).limit(limit).all()

@router.get("/{id}", response_model=EvidenceResponse)
def get_evidence_detail(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    e = db.query(Evidence).filter(Evidence.id == id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return e
