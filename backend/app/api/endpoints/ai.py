from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import AIInterpretationResponse
from app.services.ai_service import get_interpretation

router = APIRouter()

@router.get("/interpret/{entity_type}/{entity_id}", response_model=AIInterpretationResponse)
def interpret_entity(entity_type: str, entity_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    interpretation = get_interpretation(db, entity_type, entity_id)
    return interpretation
