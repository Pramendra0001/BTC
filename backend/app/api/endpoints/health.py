from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import HealthResponse, SystemStatusResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health():
    return {"status": "ok"}

from sqlalchemy import text

from app.services.geoip_service import geoip_service

@router.get("/system/status", response_model=SystemStatusResponse)
def get_system_status(db: Session = Depends(get_db)):
    db_status = "OPERATIONAL"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "ERROR"
        
    return {
        "database": db_status,
        "ml_service": "ok",
        "ai_provider": "mock",
        "uptime_seconds": 3600,
        "geoip_service": geoip_service.validate_status()
    }
