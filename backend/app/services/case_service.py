"""
BTC-SHIELD Case Management Service
Full investigative lifecycle: Alert → Review → Case → Evidence → Notes → Report.
"""
from sqlalchemy.orm import Session
from app.models.models import (
    Case, CaseEntity, CaseEvidence, CaseNote, Alert, Evidence,
    Wallet, Transaction, IPEntity, User
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_case(db: Session, title: str, description: str, priority: str,
                investigator_id: int, alert_id: int = None) -> Case:
    """Create a new investigation case, optionally from an alert."""
    case = Case(
        title=title,
        description=description,
        status="OPEN",
        priority=priority,
        investigator_id=investigator_id,
    )
    db.add(case)
    db.flush()

    # If created from an alert, auto-attach the alert's entity and evidence
    if alert_id:
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.status = "CASE_CREATED"
            alert.review_state = "REVIEWED"

            # Attach entity
            ce = CaseEntity(
                case_id=case.id,
                entity_type=alert.entity_type,
                entity_id=alert.entity_id,
            )
            db.add(ce)

            # Attach evidence
            if alert.evidence_ids:
                for ev_id in alert.evidence_ids:
                    cev = CaseEvidence(
                        case_id=case.id,
                        evidence_id=ev_id,
                    )
                    db.add(cev)

    db.commit()
    db.refresh(case)
    logger.info(f"Case created: {case.id} - {title}")
    
    from app.services import audit_service
    audit_service.log_action(
        db,
        action="CASE_CREATED",
        user_id=investigator_id,
        entity_type="CASE",
        entity_id=str(case.id),
        details={"title": title, "priority": priority, "from_alert_id": alert_id}
    )
    return case


def update_case(db: Session, case_id: int, **kwargs) -> Case:
    """Update case fields."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None

    for key, value in kwargs.items():
        if hasattr(case, key) and value is not None:
            setattr(case, key, value)

    case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case


def attach_entity(db: Session, case_id: int, entity_type: str, entity_id: str):
    """Attach an entity to a case."""
    existing = db.query(CaseEntity).filter(
        CaseEntity.case_id == case_id,
        CaseEntity.entity_type == entity_type,
        CaseEntity.entity_id == entity_id,
    ).first()

    if not existing:
        ce = CaseEntity(
            case_id=case_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )
        db.add(ce)
        db.commit()


def attach_evidence(db: Session, case_id: int, evidence_id: int):
    """Attach evidence to a case."""
    existing = db.query(CaseEvidence).filter(
        CaseEvidence.case_id == case_id,
        CaseEvidence.evidence_id == evidence_id,
    ).first()

    if not existing:
        cev = CaseEvidence(
            case_id=case_id,
            evidence_id=evidence_id,
        )
        db.add(cev)
        db.commit()


def add_note(db: Session, case_id: int, user_id: int, content: str):
    """Add an investigator note to a case."""
    note = CaseNote(
        case_id=case_id,
        user_id=user_id,
        content=content,
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def get_case_detail(db: Session, case_id: int) -> dict:
    """Get full case detail with entities, evidence, and notes."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        return None

    # Get investigator info
    investigator = db.query(User).filter(User.id == case.investigator_id).first()

    # Get attached entities
    case_entities = db.query(CaseEntity).filter(CaseEntity.case_id == case_id).all()
    entities = []
    for ce in case_entities:
        entity_info = {"type": ce.entity_type, "id": ce.entity_id, "added_at": ce.added_at.isoformat() if ce.added_at else None}
        # Enrich with basic info
        if ce.entity_type == "WALLET":
            wallet = db.query(Wallet).filter(Wallet.address == ce.entity_id).first()
            if wallet:
                entity_info["label"] = wallet.address
                entity_info["tx_count"] = wallet.tx_count
        elif ce.entity_type == "IP":
            ip = db.query(IPEntity).filter(IPEntity.ip_address == ce.entity_id).first()
            if ip:
                entity_info["label"] = ip.ip_address
                entity_info["country"] = ip.country
        entities.append(entity_info)

    # Get attached evidence
    case_evidence = db.query(CaseEvidence).filter(CaseEvidence.case_id == case_id).all()
    evidence_list = []
    for cev in case_evidence:
        ev = db.query(Evidence).filter(Evidence.id == cev.evidence_id).first()
        if ev:
            evidence_list.append({
                "id": ev.id,
                "category": ev.category,
                "observation": ev.observation,
                "strength": ev.strength,
                "entity_type": ev.entity_type,
                "entity_id": ev.entity_id,
            })

    # Get notes
    notes = db.query(CaseNote).filter(CaseNote.case_id == case_id).order_by(CaseNote.created_at.asc()).all()
    notes_list = []
    for note in notes:
        user = db.query(User).filter(User.id == note.user_id).first()
        notes_list.append({
            "id": note.id,
            "content": note.content,
            "author": user.username if user else "Unknown",
            "created_at": note.created_at.isoformat() if note.created_at else None,
        })

    return {
        "id": case.id,
        "title": case.title,
        "description": case.description,
        "status": case.status,
        "priority": case.priority,
        "investigator": investigator.username if investigator else None,
        "investigator_id": case.investigator_id,
        "created_at": case.created_at.isoformat() if case.created_at else None,
        "updated_at": case.updated_at.isoformat() if case.updated_at else None,
        "entities": entities,
        "evidence": evidence_list,
        "notes": notes_list,
        "entity_count": len(entities),
        "evidence_count": len(evidence_list),
        "note_count": len(notes_list),
    }


def generate_report(db: Session, case_id: int) -> dict:
    """Generate an investigative report for a case."""
    detail = get_case_detail(db, case_id)
    if not detail:
        return None

    report = {
        "report_type": "INVESTIGATION_REPORT",
        "generated_at": datetime.utcnow().isoformat(),
        "case": detail,
        "summary": {
            "title": detail["title"],
            "status": detail["status"],
            "priority": detail["priority"],
            "investigator": detail["investigator"],
            "total_entities": detail["entity_count"],
            "total_evidence": detail["evidence_count"],
            "total_notes": detail["note_count"],
        },
        "disclaimer": (
            "This report is generated from synthetic data for demonstration purposes. "
            "All entities, transactions, and behavioral signals are derived from "
            "algorithmic analysis. No definitive criminal determination is made. "
            "Findings represent investigative leads requiring further review."
        ),
    }

    from app.services import audit_service
    audit_service.log_action(
        db,
        action="REPORT_EXPORTED",
        user_id=detail.get("investigator_id"),
        entity_type="CASE",
        entity_id=str(case_id),
        details={"case_title": detail["title"], "entity_count": detail["entity_count"]}
    )

    return report
