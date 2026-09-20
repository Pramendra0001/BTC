from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Alert
from app.schemas.schemas import AlertListResponse, AlertDetailResponse
from typing import Optional

router = APIRouter()

@router.get("/", response_model=AlertListResponse)
def list_alerts(
    priority: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Alert)
    if priority:
        query = query.filter(Alert.priority == priority.upper())
    if status:
        query = query.filter(Alert.status == status.upper())
    total = query.count()
    alerts = query.order_by(Alert.anomaly_score.desc(), Alert.created_at.desc()).offset(skip).limit(limit).all()
    return {"alerts": alerts, "total": total}

@router.get("/{id}", response_model=AlertDetailResponse)
def get_alert_detail(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return alert

@router.get("/{id}/explain")
@router.post("/{id}/explain")
def explain_alert(id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Generate explainable AI investigation brief for an alert."""
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    from app.services.ai_service import get_interpretation
    interp = get_interpretation(db, alert.entity_type, alert.entity_id)
    interp["alert_id"] = alert.id
    interp["priority"] = alert.priority
    interp["primary_findings"] = interp.get("summary")
    interp["contributing_factors"] = interp.get("contributing_signals", [])
    interp["recommended_actions"] = interp.get("recommended_review_actions", [])
    interp["uncertainty_caveats"] = interp.get("uncertainty")
    return interp
