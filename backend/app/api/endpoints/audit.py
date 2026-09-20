"""
BTC-SHIELD Audit Log Endpoints
Allows investigators and administrators to inspect system audit trail and user actions.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import audit_service
from typing import Optional

router = APIRouter()

@router.get("")
def get_audit_trail(
    action: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    entity_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """List forensic audit trail entries with user attribution and operation metadata."""
    logs, total = audit_service.get_audit_logs(
        db, action=action, user_id=user_id, entity_type=entity_type, limit=limit, offset=offset
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "audit_logs": logs
    }
