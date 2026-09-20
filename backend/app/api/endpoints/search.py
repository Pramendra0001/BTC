from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.schemas.schemas import SearchResponse
from app.services.search_service import search

router = APIRouter()

@router.get("/", response_model=SearchResponse)
def global_search(q: str = Query(..., min_length=1), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    results = search(db, q)
    return {"query": q, "results": results}
