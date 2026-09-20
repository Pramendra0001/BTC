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
    
    resp = TransactionDetailResponse.from_orm(tx)
    resp.inputs = []
    resp.outputs = []
    return resp
