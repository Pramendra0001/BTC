from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Transaction
from app.schemas.schemas import TransactionResponse, TransactionDetailResponse
from typing import List

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Transaction).offset(skip).limit(limit).all()

@router.get("/{txid}", response_model=TransactionDetailResponse)
def get_transaction(txid: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tx = db.query(Transaction).filter(Transaction.txid == txid).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
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
            for inp in tx.inputs
        ],
        outputs=[
            {
                "wallet_address": out.wallet_address,
                "amount": out.amount or 0.0,
                "position": out.position or 0
            }
            for out in tx.outputs
        ]
    )
