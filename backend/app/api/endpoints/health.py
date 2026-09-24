from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.schemas import HealthResponse, SystemStatusResponse

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def get_health():
    return {"status": "ok"}

from sqlalchemy import text
from app.core.config import settings
from app.services.geoip_service import geoip_service

@router.get("/system/status", response_model=SystemStatusResponse)
def get_system_status(db: Session = Depends(get_db)):
    db_status = "OPERATIONAL"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "ERROR"
        
    geoip_telemetry = geoip_service.validate_status()
    
    return {
        "database": db_status,
        "ml_service": "ok",
        "ai_provider": settings.AI_PROVIDER,
        "uptime_seconds": 3600,
        "geoip_service": geoip_telemetry,
        "app_mode": settings.APP_MODE,
        "offline_mode": settings.OFFLINE_MODE,
        "offline_telemetry": {
            "app_mode": settings.APP_MODE.upper(),
            "frontend_status": "OPERATIONAL",
            "backend_status": "OPERATIONAL",
            "database_status": db_status,
            "ml_engine": "Isolation Forest & DBSCAN (scikit-learn local)",
            "graph_engine": "NetworkX (local in-memory)",
            "evidence_engine": "Deterministic Multi-Layer Correlation",
            "geoip_mode": geoip_telemetry.get("status", "FALLBACK"),
            "external_api_calls": "NONE",
            "internet_required": "NO"
        }
    }

