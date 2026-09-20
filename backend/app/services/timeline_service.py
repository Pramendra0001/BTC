"""
BTC-SHIELD Timeline Service
Generates chronological event timelines for entities.
"""
from sqlalchemy.orm import Session
from app.models.models import (
    Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, Alert, Evidence, AnomalyResult
)
import logging

logger = logging.getLogger(__name__)


def get_entity_timeline(db: Session, entity_type: str, entity_id: str) -> list[dict]:
    """Get chronological timeline of events for an entity."""
    events = []

    if entity_type == "WALLET":
        # Transaction events
        inputs = db.query(TransactionInput).filter(
            TransactionInput.wallet_address == entity_id
        ).all()
        outputs = db.query(TransactionOutput).filter(
            TransactionOutput.wallet_address == entity_id
        ).all()

        tx_ids = set(i.transaction_id for i in inputs) | set(o.transaction_id for o in outputs)
        if tx_ids:
            txs = db.query(Transaction).filter(Transaction.id.in_(tx_ids)).all()
            for tx in txs:
                direction = "SENT" if any(i.transaction_id == tx.id for i in inputs) else "RECEIVED"
                events.append({
                    "type": "TRANSACTION",
                    "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                    "title": f"Transaction {direction}",
                    "description": f"TXID: {tx.txid[:16]}... | Amount: {tx.total_input:.0f} sat | Fee: {tx.fee:.0f} sat",
                    "entity_type": "TRANSACTION",
                    "entity_id": tx.txid,
                    "details": {
                        "txid": tx.txid,
                        "direction": direction,
                        "total_input": tx.total_input,
                        "total_output": tx.total_output,
                        "fee": tx.fee,
                    }
                })

        # Network observations
        txids = [tx.txid for tx in db.query(Transaction).filter(Transaction.id.in_(tx_ids)).all()] if tx_ids else []
        if txids:
            observations = db.query(NetworkObservation).filter(
                NetworkObservation.transaction_id.in_(txids)
            ).all()
            for obs in observations:
                events.append({
                    "type": "NETWORK_OBSERVATION",
                    "timestamp": obs.timestamp.isoformat() if obs.timestamp else None,
                    "title": "Network Observation",
                    "description": f"IP: {obs.src_ip} → {obs.dst_ip} | ASN: {obs.asn} | Country: {obs.geo_country}",
                    "entity_type": "IP",
                    "entity_id": obs.src_ip,
                    "details": {
                        "src_ip": obs.src_ip,
                        "dst_ip": obs.dst_ip,
                        "asn": obs.asn,
                        "geo_country": obs.geo_country,
                    }
                })

    elif entity_type == "IP":
        observations = db.query(NetworkObservation).filter(
            NetworkObservation.src_ip == entity_id
        ).all()
        for obs in observations:
            events.append({
                "type": "NETWORK_OBSERVATION",
                "timestamp": obs.timestamp.isoformat() if obs.timestamp else None,
                "title": "Network Observation",
                "description": f"TX: {obs.transaction_id[:16]}... → {obs.dst_ip} | ASN: {obs.asn}",
                "entity_type": "TRANSACTION",
                "entity_id": obs.transaction_id,
                "details": {
                    "transaction_id": obs.transaction_id,
                    "dst_ip": obs.dst_ip,
                    "asn": obs.asn,
                    "geo_country": obs.geo_country,
                }
            })

    elif entity_type == "TX" or entity_type == "TRANSACTION":
        tx = db.query(Transaction).filter(Transaction.txid == entity_id).first()
        if tx:
            events.append({
                "type": "TRANSACTION",
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "title": "Transaction Created",
                "description": f"Inputs: {tx.total_input:.0f} | Outputs: {tx.total_output:.0f} | Fee: {tx.fee:.0f}",
                "entity_type": "TRANSACTION",
                "entity_id": tx.txid,
                "details": {"txid": tx.txid},
            })

    # Add alerts as timeline events
    alerts = db.query(Alert).filter(
        Alert.entity_type == entity_type,
        Alert.entity_id == entity_id
    ).all()
    for alert in alerts:
        events.append({
            "type": "ALERT",
            "timestamp": alert.created_at.isoformat() if alert.created_at else None,
            "title": f"Alert Generated ({alert.priority})",
            "description": f"Anomaly Score: {alert.anomaly_score:.1f} | Confidence: {alert.confidence:.2f}",
            "entity_type": "ALERT",
            "entity_id": str(alert.id),
            "details": {
                "priority": alert.priority,
                "anomaly_score": alert.anomaly_score,
                "confidence": alert.confidence,
            }
        })

    # Sort by timestamp
    events.sort(key=lambda e: e.get("timestamp") or "")

    return events
