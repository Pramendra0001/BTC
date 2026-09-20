from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import (
    User, Wallet, Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, Alert, Evidence, BehavioralFeature, AnomalyResult
)

router = APIRouter()


@router.get("/")
def list_wallets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List wallets with pagination."""
    total = db.query(Wallet).count()
    wallets = db.query(Wallet).offset(skip).limit(limit).all()
    return {
        "wallets": [
            {
                "address": w.address,
                "tx_count": w.tx_count,
                "total_sent": w.total_sent,
                "total_received": w.total_received,
                "first_seen": w.first_seen.isoformat() if w.first_seen else None,
                "last_seen": w.last_seen.isoformat() if w.last_seen else None,
            }
            for w in wallets
        ],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/{address}")
def get_wallet(
    address: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get full wallet intelligence detail."""
    wallet = db.query(Wallet).filter(Wallet.address == address).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Transactions
    inputs = db.query(TransactionInput).filter(
        TransactionInput.wallet_address == address
    ).all()
    outputs = db.query(TransactionOutput).filter(
        TransactionOutput.wallet_address == address
    ).all()

    tx_ids = set(i.transaction_id for i in inputs) | set(o.transaction_id for o in outputs)
    transactions = []
    if tx_ids:
        txs = db.query(Transaction).filter(Transaction.id.in_(tx_ids)).order_by(Transaction.timestamp.desc()).limit(50).all()
        for tx in txs:
            direction = "SENT" if any(i.transaction_id == tx.id for i in inputs) else "RECEIVED"
            transactions.append({
                "txid": tx.txid,
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "direction": direction,
                "total_input": tx.total_input,
                "total_output": tx.total_output,
                "fee": tx.fee,
                "script_type": tx.script_type,
            })

    # Network observations
    txids = [tx.txid for tx in db.query(Transaction).filter(Transaction.id.in_(tx_ids)).all()] if tx_ids else []
    observations = []
    if txids:
        obs_list = db.query(NetworkObservation).filter(
            NetworkObservation.transaction_id.in_(txids)
        ).limit(50).all()
        observations = [
            {
                "src_ip": o.src_ip,
                "dst_ip": o.dst_ip,
                "asn": o.asn,
                "country": o.geo_country,
                "timestamp": o.timestamp.isoformat() if o.timestamp else None,
            }
            for o in obs_list
        ]

    # Counterparties
    counterparty_addrs = set()
    for inp in inputs:
        cp_outputs = db.query(TransactionOutput).filter(
            TransactionOutput.transaction_id == inp.transaction_id,
            TransactionOutput.wallet_address != address
        ).all()
        for o in cp_outputs:
            counterparty_addrs.add(o.wallet_address)
    for out in outputs:
        cp_inputs = db.query(TransactionInput).filter(
            TransactionInput.transaction_id == out.transaction_id,
            TransactionInput.wallet_address != address
        ).all()
        for i in cp_inputs:
            counterparty_addrs.add(i.wallet_address)

    # Alerts
    alerts = db.query(Alert).filter(
        Alert.entity_type == "WALLET",
        Alert.entity_id == address
    ).all()
    alert_list = [
        {
            "id": a.id,
            "priority": a.priority,
            "anomaly_score": a.anomaly_score,
            "confidence": a.confidence,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in alerts
    ]

    # Evidence
    evidence = db.query(Evidence).filter(
        Evidence.entity_type == "WALLET",
        Evidence.entity_id == address
    ).all()
    evidence_list = [
        {
            "id": e.id,
            "category": e.category,
            "observation": e.observation,
            "strength": e.strength,
        }
        for e in evidence
    ]

    # Behavioral features
    bf = db.query(BehavioralFeature).filter(
        BehavioralFeature.entity_type == "WALLET",
        BehavioralFeature.entity_id == address
    ).first()

    # Anomaly result
    anomaly = db.query(AnomalyResult).filter(
        AnomalyResult.entity_type == "WALLET",
        AnomalyResult.entity_id == address
    ).order_by(AnomalyResult.created_at.desc()).first()

    return {
        "address": wallet.address,
        "first_seen": wallet.first_seen.isoformat() if wallet.first_seen else None,
        "last_seen": wallet.last_seen.isoformat() if wallet.last_seen else None,
        "tx_count": wallet.tx_count,
        "total_sent": wallet.total_sent,
        "total_received": wallet.total_received,
        "net_flow": (wallet.total_received or 0) - (wallet.total_sent or 0),
        "transactions": transactions,
        "network_observations": observations,
        "counterparties": list(counterparty_addrs)[:50],
        "counterparty_count": len(counterparty_addrs),
        "alerts": alert_list,
        "evidence": evidence_list,
        "features": bf.features if bf else None,
        "anomaly_score": anomaly.anomaly_score if anomaly else None,
        "cluster_id": anomaly.cluster_id if anomaly else None,
    }
