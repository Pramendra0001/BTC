from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import SearchResponse
from app.services.search_service import search
from typing import Optional

router = APIRouter()

@router.get("/", response_model=SearchResponse)
def global_search(
    q: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    search_term = q or query or ""
    if not search_term or len(search_term.strip()) < 1:
        return {"query": search_term, "total": 0, "results": []}
    return search(db, search_term)
