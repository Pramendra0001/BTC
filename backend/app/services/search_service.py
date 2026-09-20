"""
BTC-SHIELD Search Service
Global search across wallets, transactions, IPs, ASNs, alerts, and cases.
"""
from sqlalchemy.orm import Session
from app.models.models import Wallet, Transaction, IPEntity, ASNEntity, Alert, Case
import logging

logger = logging.getLogger(__name__)


def search(db: Session, query: str, limit: int = 20) -> dict:
    """Search across all entity types. Returns categorized results."""
    if not query or len(query) < 2:
        return {"results": [], "total": 0, "query": query}

    results = []
    q = query.strip()

    # Search wallets
    wallets = db.query(Wallet).filter(
        Wallet.address.ilike(f"%{q}%")
    ).limit(limit).all()
    for w in wallets:
        results.append({
            "type": "WALLET",
            "id": w.address,
            "label": w.address,
            "subtitle": f"TX: {w.tx_count} | Sent: {w.total_sent:.0f} | Received: {w.total_received:.0f}",
            "url": f"/wallets/{w.address}",
        })

    # Search transactions
    txs = db.query(Transaction).filter(
        Transaction.txid.ilike(f"%{q}%")
    ).limit(limit).all()
    for tx in txs:
        results.append({
            "type": "TRANSACTION",
            "id": tx.txid,
            "label": tx.txid,
            "subtitle": f"Amount: {tx.total_input:.0f} sat | Fee: {tx.fee:.0f} sat",
            "url": f"/transactions/{tx.txid}",
        })

    # Search IPs
    ips = db.query(IPEntity).filter(
        IPEntity.ip_address.ilike(f"%{q}%")
    ).limit(limit).all()
    for ip in ips:
        results.append({
            "type": "IP",
            "id": ip.ip_address,
            "label": ip.ip_address,
            "subtitle": f"ASN: {ip.asn} | Country: {ip.country} | Observations: {ip.observation_count}",
            "url": f"/ips/{ip.ip_address}",
        })

    # Search ASNs
    asns = db.query(ASNEntity).filter(
        ASNEntity.asn_number.ilike(f"%{q}%")
    ).limit(limit).all()
    for asn in asns:
        results.append({
            "type": "ASN",
            "id": asn.asn_number,
            "label": asn.asn_number,
            "subtitle": f"IPs: {asn.ip_count} | Countries: {asn.country_count}",
            "url": f"/asns/{asn.asn_number}",
        })

    # Search cases
    cases = db.query(Case).filter(
        Case.title.ilike(f"%{q}%")
    ).limit(limit).all()
    for c in cases:
        results.append({
            "type": "CASE",
            "id": str(c.id),
            "label": c.title,
            "subtitle": f"Status: {c.status} | Priority: {c.priority}",
            "url": f"/cases/{c.id}",
        })

    return {
        "results": results,
        "total": len(results),
        "query": query,
    }
