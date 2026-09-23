"""
BTC-SHIELD Search Service
Global search across wallets, transactions, IPs, ASNs, alerts, and cases.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from app.models.models import Wallet, Transaction, IPEntity, ASNEntity, Alert, Case, RawRecord, GraphEdge
import logging

logger = logging.getLogger(__name__)


def search(db: Session, query: str, limit: int = 5) -> dict:
    """Search across all entity types with indexed prefix matching and strict limits."""
    if not query or len(query.strip()) < 2:
        return {"results": [], "total": 0, "query": query}

    results = []
    q = query.strip()
    cat_limit = min(limit, 5)

    # 1. Search wallets using indexed prefix first
    wallets = db.query(Wallet).filter(
        Wallet.address.ilike(f"{q}%")
    ).limit(cat_limit).all()

    if len(wallets) < cat_limit and len(q) >= 4:
        sub_wallets = db.query(Wallet).filter(
            Wallet.address.ilike(f"%{q}%")
        ).limit(cat_limit - len(wallets)).all()
        wallets = list({w.address: w for w in (wallets + sub_wallets)}.values())

    for w in wallets:
        total_sent = w.total_sent or 0.0
        total_recv = w.total_received or 0.0
        results.append({
            "type": "WALLET",
            "id": w.address,
            "label": w.address,
            "subtitle": f"TX: {w.tx_count or 0} | Sent: {total_sent:.0f} | Received: {total_recv:.0f}",
            "url": f"/wallets/{w.address}",
        })

    # 2. Search transactions using normalized prefix and substring
    q_tx = q
    for p in ["TX:", "tx:", "TRANSACTION:", "transaction:"]:
        if q_tx.startswith(p):
            q_tx = q_tx[len(p):].strip()

    txs = db.query(Transaction).filter(
        or_(
            Transaction.txid.ilike(f"{q_tx}%"),
            Transaction.txid.ilike(f"TX:{q_tx}%")
        )
    ).limit(cat_limit).all()

    if len(txs) < cat_limit and len(q_tx) >= 6:
        sub_txs = db.query(Transaction).filter(
            Transaction.txid.ilike(f"%{q_tx}%")
        ).limit(cat_limit - len(txs)).all()
        txs = list({t.txid: t for t in (txs + sub_txs)}.values())

    seen_txids = set()
    for tx in txs:
        clean_id = tx.txid.replace("TX:", "").replace("TRANSACTION:", "")
        if clean_id not in seen_txids:
            seen_txids.add(clean_id)
            results.append({
                "type": "TRANSACTION",
                "id": clean_id,
                "label": clean_id,
                "subtitle": f"Amount: {tx.total_input or 0:.0f} sat | Fee: {tx.fee or 0:.0f} sat",
                "url": f"/transactions/{clean_id}",
            })

    # If no transactions found yet, check RawRecord (audit logs)
    if len(seen_txids) < cat_limit and len(q_tx) >= 4:
        raw_txs = db.query(RawRecord).filter(
            cast(RawRecord.raw_data, String).like(f'%{q_tx}%')
        ).limit(cat_limit - len(seen_txids)).all()
        for r in raw_txs:
            if isinstance(r.raw_data, dict) and r.raw_data.get("txid"):
                raw_txid = str(r.raw_data["txid"]).replace("TX:", "").replace("TRANSACTION:", "")
                if raw_txid not in seen_txids:
                    seen_txids.add(raw_txid)
                    results.append({
                        "type": "TRANSACTION",
                        "id": raw_txid,
                        "label": raw_txid,
                        "subtitle": f"Fee: {r.raw_data.get('fee', 0)} | Script: {r.raw_data.get('script_type', 'p2pkh')}",
                        "url": f"/transactions/{raw_txid}",
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
