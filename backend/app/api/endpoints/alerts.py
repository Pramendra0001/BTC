from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Alert
from app.schemas.schemas import AlertListResponse, AlertDetailResponse
from typing import Optional

router = APIRouter()

@router.get("/", response_model=AlertListResponse)
def list_alerts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alerts = db.query(Alert).offset(skip).limit(limit).all()
    total = db.query(Alert).count()
    return {"alerts": alerts, "total": total}

@router.get("/{id}", response_model=AlertDetailResponse)
def get_alert_detail(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert
