"""
BTC-SHIELD Audit Service
Records immutable audit logs for user actions, investigations, data operations, and exports.
"""
from sqlalchemy.orm import Session
from app.models.models import AuditLog, User
from datetime import datetime
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)

def log_action(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[dict[str, Any]] = None,
    ip_address: Optional[str] = None
) -> AuditLog:
    """Record an action into the audit trail."""
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=str(entity_id) if entity_id is not None else None,
            details=details or {},
            ip_address=ip_address or "127.0.0.1",
            created_at=datetime.utcnow()
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    except Exception as e:
        logger.error(f"Failed to record audit log: {e}")
        db.rollback()
        return None

def get_audit_logs(
    db: Session,
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
) -> tuple[list[dict], int]:
    """Retrieve audit logs with optional filtering and user join."""
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)

    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    # Pre-fetch user usernames
    user_ids = {l.user_id for l in logs if l.user_id}
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_map = {u.id: u.username for u in users}

    formatted_logs = [
        {
            "id": l.id,
            "user_id": l.user_id,
            "username": user_map.get(l.user_id, "System / Automated"),
            "action": l.action,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "details": l.details,
            "ip_address": l.ip_address,
            "timestamp": l.created_at.isoformat() if l.created_at else None
        }
        for l in logs
    ]

    return formatted_logs, total
