from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from sqlalchemy import or_
from app.models.models import (
    User, Wallet, Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, Alert, Evidence, BehavioralFeature, AnomalyResult, GraphEdge
)

router = APIRouter()


@router.get("/")
def list_wallets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List wallets with pagination and indexed prefix search."""
    from sqlalchemy import func
    query = db.query(Wallet)
    if search and len(search.strip()) >= 2:
        s = search.strip()
        query = query.filter(Wallet.address.ilike(f"{s}%"))

    total = query.with_entities(func.count(Wallet.id)).scalar() or 0
    wallets = query.order_by(Wallet.tx_count.desc().nullslast(), Wallet.id.desc()).offset(skip).limit(limit).all()
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
    """Get full wallet intelligence detail without N+1 query overhead."""
    wallet = db.query(Wallet).filter(Wallet.address == address).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    # Bounded inputs and outputs for this wallet
    inputs = db.query(TransactionInput).filter(
        TransactionInput.wallet_address == address
    ).limit(50).all()
    outputs = db.query(TransactionOutput).filter(
        TransactionOutput.wallet_address == address
    ).limit(50).all()

    tx_ids = list(set(i.transaction_id for i in inputs if i.transaction_id) | set(o.transaction_id for o in outputs if o.transaction_id))
    transactions = []
    txids_list = []

    if tx_ids:
        txs = db.query(Transaction).filter(
            Transaction.id.in_(tx_ids)
        ).order_by(Transaction.timestamp.desc().nullslast()).limit(50).all()

        for tx in txs:
            if tx.txid:
                txids_list.append(tx.txid)
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
    else:
        # Check GraphEdge (relational mode / Dataset 6)
        wallet_keys = [address, f"WALLET:{address}"]
        direct_edges = db.query(GraphEdge).filter(
            or_(
                GraphEdge.source_id.in_(wallet_keys),
                GraphEdge.target_id.in_(wallet_keys)
            )
        ).limit(100).all()

        connected_txids_dir = {}
        for ge in direct_edges:
            s_id = ge.source_id or ""
            t_id = ge.target_id or ""
            if ge.edge_type == "COUNTERPARTY":
                for cid in [s_id, t_id]:
                    clean_cp = cid.replace("WALLET:", "").strip()
                    if clean_cp and clean_cp != address:
                        counterparty_addrs.add(clean_cp)
            if s_id in wallet_keys:
                clean_t = t_id.replace("TX:", "").replace("TRANSACTION:", "").strip()
                if clean_t and clean_t not in wallet_keys:
                    connected_txids_dir[clean_t] = "SENT"
            elif t_id in wallet_keys:
                clean_s = s_id.replace("TX:", "").replace("TRANSACTION:", "").strip()
                if clean_s and clean_s not in wallet_keys:
                    connected_txids_dir[clean_s] = "RECEIVED"

        if connected_txids_dir:
            c_txids = list(connected_txids_dir.keys())[:50]
            txs = db.query(Transaction).filter(
                Transaction.txid.in_(c_txids)
            ).order_by(Transaction.timestamp.desc().nullslast()).limit(50).all()

            found_txids = set()
            for tx in txs:
                if tx.txid:
                    txids_list.append(tx.txid)
                    found_txids.add(tx.txid)
                direction = connected_txids_dir.get(tx.txid, "SENT")
                transactions.append({
                    "txid": tx.txid,
                    "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                    "direction": direction,
                    "total_input": tx.total_input,
                    "total_output": tx.total_output,
                    "fee": tx.fee,
                    "script_type": tx.script_type or "p2wpkh",
                })

            for ctxid, cdir in connected_txids_dir.items():
                if ctxid not in found_txids and len(transactions) < 50:
                    txids_list.append(ctxid)
                    transactions.append({
                        "txid": ctxid,
                        "timestamp": wallet.last_seen.isoformat() if wallet.last_seen else None,
                        "direction": cdir,
                        "total_input": 0.0,
                        "total_output": 0.0,
                        "fee": 0.0,
                        "script_type": "p2wpkh",
                    })

    # Network observations (uses already-collected txids, avoiding repeated Transaction query)
    observations = []
    if txids_list:
        obs_list = db.query(NetworkObservation).filter(
            NetworkObservation.transaction_id.in_(txids_list[:50])
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

    # Counterparties via 2 bulk queries (completely eliminates N+1 query loop)
    counterparty_addrs = set()
    if tx_ids:
        cp_out_rows = db.query(TransactionOutput.wallet_address).filter(
            TransactionOutput.transaction_id.in_(tx_ids),
            TransactionOutput.wallet_address != address,
            TransactionOutput.wallet_address.isnot(None)
        ).limit(100).all()
        for (cp_addr,) in cp_out_rows:
            if cp_addr:
                counterparty_addrs.add(cp_addr)

        cp_in_rows = db.query(TransactionInput.wallet_address).filter(
            TransactionInput.transaction_id.in_(tx_ids),
            TransactionInput.wallet_address != address,
            TransactionInput.wallet_address.isnot(None)
        ).limit(100).all()
        for (cp_addr,) in cp_in_rows:
            if cp_addr:
                counterparty_addrs.add(cp_addr)

    # Alerts (bounded to 20)
    alerts = db.query(Alert).filter(
        Alert.entity_type == "WALLET",
        Alert.entity_id == address
    ).limit(20).all()
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

    # Evidence (bounded to 20)
    evidence = db.query(Evidence).filter(
        Evidence.entity_type == "WALLET",
        Evidence.entity_id == address
    ).limit(20).all()
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
    ).order_by(BehavioralFeature.computed_at.desc()).first()

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
