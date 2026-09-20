from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User
from app.services.graph_service import get_subgraph, get_path

router = APIRouter()


@router.get("/{entity_type}/{entity_id}")
def get_entity_graph(
    entity_type: str,
    entity_id: str,
    hops: int = Query(default=1, ge=1, le=3),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the subgraph around a specific entity (k-hop expansion)."""
    result = get_subgraph(db, entity_type.upper(), entity_id, hops=hops)
    return result


@router.get("/path/{src_type}/{src_id}/{tgt_type}/{tgt_id}")
def find_path(
    src_type: str, src_id: str,
    tgt_type: str, tgt_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Find shortest path between two entities."""
    return get_path(db, src_type.upper(), src_id, tgt_type.upper(), tgt_id)
