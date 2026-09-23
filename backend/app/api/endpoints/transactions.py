from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Transaction, TransactionInput, TransactionOutput
from app.schemas.schemas import TransactionResponse, TransactionDetailResponse
from typing import List, Optional

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List transactions with strict bounded pagination and indexed ordering."""
    query = db.query(Transaction)
    if search and len(search.strip()) >= 3:
        query = query.filter(Transaction.txid.ilike(f"{search.strip()}%"))

    return query.order_by(
        Transaction.timestamp.desc().nullslast(),
        Transaction.id.desc()
    ).offset(skip).limit(limit).all()

@router.get("/{txid}", response_model=TransactionDetailResponse)
def get_transaction(txid: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get single transaction with bounded inputs and outputs."""
    tx = db.query(Transaction).filter(Transaction.txid == txid).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")

    inps = db.query(TransactionInput).filter(TransactionInput.transaction_id == tx.id).order_by(TransactionInput.position.asc()).limit(100).all()
    outs = db.query(TransactionOutput).filter(TransactionOutput.transaction_id == tx.id).order_by(TransactionOutput.position.asc()).limit(100).all()

    return TransactionDetailResponse(
        id=tx.id,
        txid=tx.txid,
        timestamp=tx.timestamp,
        fee=tx.fee or 0.0,
        script_type=tx.script_type or "",
        total_input=tx.total_input or 0.0,
        total_output=tx.total_output or 0.0,
        inputs=[
            {
                "wallet_address": inp.wallet_address,
                "amount": inp.amount or 0.0,
                "position": inp.position or 0
            }
            for inp in inps
        ],
        outputs=[
            {
                "wallet_address": out.wallet_address,
                "amount": out.amount or 0.0,
                "position": out.position or 0
            }
            for out in outs
        ]
    )
