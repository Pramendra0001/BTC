from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Case, Alert
from app.services.case_service import (
    create_case, update_case, attach_entity,
    attach_evidence, add_note, get_case_detail, generate_report
)

router = APIRouter()


class CaseCreate(BaseModel):
    title: str
    description: str = ""
    priority: str = "MEDIUM"
    alert_id: Optional[int] = None


class CaseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class EntityAttach(BaseModel):
    entity_type: str
    entity_id: str


class EvidenceAttach(BaseModel):
    evidence_id: int


class NoteCreate(BaseModel):
    content: str


@router.get("/")
def list_cases(
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Case)
    if status:
        query = query.filter(Case.status == status)
    total = query.count()
    cases = query.order_by(Case.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "cases": [
            {
                "id": c.id,
                "title": c.title,
                "status": c.status,
                "priority": c.priority,
                "investigator_id": c.investigator_id,
                "created_at": c.created_at.isoformat() if c.created_at else None,
                "updated_at": c.updated_at.isoformat() if c.updated_at else None,
            }
            for c in cases
        ],
        "total": total,
    }


@router.post("/")
def create_new_case(
    body: CaseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = create_case(
        db, body.title, body.description, body.priority,
        current_user.id, body.alert_id
    )
    return {"id": case.id, "title": case.title, "status": case.status}


@router.get("/{case_id}")
def get_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    detail = get_case_detail(db, case_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Case not found")
    return detail


@router.patch("/{case_id}")
def patch_case(
    case_id: int,
    body: CaseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    case = update_case(db, case_id, **body.model_dump(exclude_none=True))
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return {"id": case.id, "status": case.status}


@router.post("/{case_id}/entities")
def add_entity(
    case_id: int,
    body: EntityAttach,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attach_entity(db, case_id, body.entity_type, body.entity_id)
    return {"message": "Entity attached"}


@router.post("/{case_id}/evidence")
def add_evidence(
    case_id: int,
    body: EvidenceAttach,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    attach_evidence(db, case_id, body.evidence_id)
    return {"message": "Evidence attached"}


@router.post("/{case_id}/notes")
def create_note(
    case_id: int,
    body: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    note = add_note(db, case_id, current_user.id, body.content)
    return {"id": note.id, "content": note.content}


@router.get("/{case_id}/report")
def get_report(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    report = generate_report(db, case_id)
    if not report:
        raise HTTPException(status_code=404, detail="Case not found")
    return report
