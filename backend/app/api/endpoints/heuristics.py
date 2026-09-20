"""
BTC-SHIELD Structural Heuristics Endpoints
Exposes detected peeling chains, CoinJoin/mixing patterns, and single-tx structural inspections.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services import heuristics_service

router = APIRouter()

@router.get("/summary")
def get_heuristics_summary(db: Session = Depends(get_db)):
    """Summary of all structural heuristics across the ingested transactions."""
    return heuristics_service.get_heuristics_summary(db)

@router.get("/peeling-chains")
def get_peeling_chains(
    min_hops: int = Query(2, ge=1, le=20),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve detected peeling chains ordered by hop count and volume."""
    return heuristics_service.detect_peeling_chains(db, min_hops=min_hops, limit=limit)

@router.get("/mixing-patterns")
def get_mixing_patterns(
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """Retrieve detected CoinJoin and mixing/tumbler transactions."""
    return heuristics_service.detect_mixing_patterns(db, limit=limit)

@router.get("/transaction/{txid}")
def analyze_transaction(
    txid: str,
    db: Session = Depends(get_db)
):
    """Detailed structural heuristic analysis for a specific transaction ID."""
    result = heuristics_service.analyze_transaction_heuristics(db, txid)
    if not result.get("found"):
        raise HTTPException(status_code=404, detail="Transaction not found")
    return result
