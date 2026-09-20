from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import TimelineResponse
from app.services.timeline_service import get_entity_timeline

router = APIRouter()

@router.get("/{entity_type}/{entity_id}", response_model=TimelineResponse)
def get_timeline(entity_type: str, entity_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    events = get_entity_timeline(db, entity_type, entity_id)
    return {"entity_type": entity_type, "entity_id": entity_id, "events": events}
