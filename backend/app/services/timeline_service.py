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

    e_type = entity_type.upper() if entity_type else ""

    if e_type == "WALLET":
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
                in_str = f"{tx.total_input:.0f}" if tx.total_input is not None else "0"
                fee_str = f"{tx.fee:.0f}" if tx.fee is not None else "0"
                events.append({
                    "type": "TRANSACTION",
                    "event_type": "TRANSACTION",
                    "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                    "title": f"Transaction {direction}",
                    "description": f"TXID: {tx.txid[:16]}... | Amount: {in_str} sat | Fee: {fee_str} sat",
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
                    "event_type": "NETWORK_OBSERVATION",
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

    elif e_type == "IP":
        observations = db.query(NetworkObservation).filter(
            NetworkObservation.src_ip == entity_id
        ).all()
        for obs in observations:
            events.append({
                "type": "NETWORK_OBSERVATION",
                "event_type": "NETWORK_OBSERVATION",
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

    elif e_type in ("TX", "TRANSACTION"):
        tx = db.query(Transaction).filter(Transaction.txid == entity_id).first()
        if tx:
            in_str = f"{tx.total_input:.0f}" if tx.total_input is not None else "0"
            out_str = f"{tx.total_output:.0f}" if tx.total_output is not None else "0"
            fee_str = f"{tx.fee:.0f}" if tx.fee is not None else "0"
            events.append({
                "type": "TRANSACTION",
                "event_type": "TRANSACTION",
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "title": "Transaction Created",
                "description": f"Inputs: {in_str} | Outputs: {out_str} | Fee: {fee_str}",
                "entity_type": "TRANSACTION",
                "entity_id": tx.txid,
                "details": {"txid": tx.txid},
            })

    # Add alerts as timeline events
    alerts = db.query(Alert).filter(
        Alert.entity_type == e_type,
        Alert.entity_id == entity_id
    ).all()
    for alert in alerts:
        score_str = f"{alert.anomaly_score:.1f}" if alert.anomaly_score is not None else "N/A"
        conf_str = f"{alert.confidence:.2f}" if alert.confidence is not None else "N/A"
        events.append({
            "type": "ALERT",
            "event_type": "ALERT",
            "timestamp": alert.created_at.isoformat() if alert.created_at else None,
            "title": f"Alert Generated ({alert.priority})",
            "description": f"Anomaly Score: {score_str} | Confidence: {conf_str}",
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
