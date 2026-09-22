"""
BTC-SHIELD Entity Resolution Service
Re-resolves and updates entity statistics from existing data.
Primary entity creation happens during ingestion; this service handles
post-ingestion bulk aggregation, IP entity discovery, and ASN entity aggregation.
High performance: zero N+1 queries, fully vectorized in-memory mappings.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import (
    Wallet, IPEntity, ASNEntity, Transaction,
    TransactionInput, TransactionOutput, NetworkObservation
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def resolve_wallets(db: Session):
    """Re-compute wallet aggregate statistics in high-performance bulk operations."""
    # Check if TransactionInput or TransactionOutput exist
    ti_count = db.query(TransactionInput.id).limit(1).count()
    to_count = db.query(TransactionOutput.id).limit(1).count()

    if ti_count == 0 and to_count == 0:
        logger.info("TransactionInput/Output tables empty (relational mode); wallet aggregates preserved from ingestion.")
        return

    logger.info("Re-resolving wallet aggregates in bulk from transaction inputs and outputs...")
    
    # 1. Bulk aggregate inputs
    input_stats = db.query(
        TransactionInput.wallet_address,
        func.coalesce(func.sum(TransactionInput.amount), 0).label("total_sent"),
        func.count(func.distinct(TransactionInput.transaction_id)).label("tx_in_count")
    ).group_by(TransactionInput.wallet_address).all()
    in_map = {row[0]: (float(row[1] or 0), int(row[2] or 0)) for row in input_stats if row[0]}

    # 2. Bulk aggregate outputs
    output_stats = db.query(
        TransactionOutput.wallet_address,
        func.coalesce(func.sum(TransactionOutput.amount), 0).label("total_received"),
        func.count(func.distinct(TransactionOutput.transaction_id)).label("tx_out_count")
    ).group_by(TransactionOutput.wallet_address).all()
    out_map = {row[0]: (float(row[1] or 0), int(row[2] or 0)) for row in output_stats if row[0]}

    wallets = db.query(Wallet).all()
    for w in wallets:
        in_sent, in_txs = in_map.get(w.address, (0.0, 0))
        out_recv, out_txs = out_map.get(w.address, (0.0, 0))
        if in_sent > 0 or out_recv > 0 or in_txs > 0 or out_txs > 0:
            w.total_sent = in_sent
            w.total_received = out_recv
            w.tx_count = max(w.tx_count or 0, in_txs + out_txs)

    db.commit()
    logger.info("Wallet re-resolution complete.")


def resolve_ips(db: Session):
    """Populate and re-compute IP entity statistics from network observations in bulk."""
    logger.info("Resolving IP entities from network observations in bulk...")

    # Aggregate NetworkObservation by src_ip
    obs_stats = db.query(
        NetworkObservation.src_ip,
        func.count(NetworkObservation.id).label("obs_count"),
        func.min(NetworkObservation.timestamp).label("first_seen"),
        func.max(NetworkObservation.timestamp).label("last_seen"),
        func.max(NetworkObservation.asn).label("asn"),
        func.max(NetworkObservation.geo_country).label("country")
    ).filter(
        NetworkObservation.src_ip.isnot(None),
        NetworkObservation.src_ip != ""
    ).group_by(NetworkObservation.src_ip).all()

    if not obs_stats:
        logger.info("No network observations to resolve IPs from.")
        return

    existing_ips = {ip.ip_address: ip for ip in db.query(IPEntity).all()}
    new_ip_entities = []

    for row in obs_stats:
        ip_addr = row[0]
        obs_count = int(row[1] or 0)
        first_seen = row[2]
        last_seen = row[3]
        asn = row[4] or ""
        country = row[5] or ""

        if ip_addr in existing_ips:
            ip_ent = existing_ips[ip_addr]
            ip_ent.observation_count = obs_count
            ip_ent.first_seen = first_seen
            ip_ent.last_seen = last_seen
            ip_ent.asn = asn
            ip_ent.country = country
        else:
            ip_ent = IPEntity(
                ip_address=ip_addr,
                observation_count=obs_count,
                first_seen=first_seen,
                last_seen=last_seen,
                asn=asn,
                country=country,
                created_at=datetime.utcnow()
            )
            new_ip_entities.append(ip_ent)

    if new_ip_entities:
        for i in range(0, len(new_ip_entities), 5000):
            db.bulk_save_objects(new_ip_entities[i:i+5000])
            db.commit()
    else:
        db.commit()

    logger.info(f"IP resolution complete: {len(obs_stats)} unique IPs resolved.")


def resolve_asns(db: Session):
    """Populate and re-compute ASN entity statistics in bulk."""
    logger.info("Resolving ASN entities from network observations in bulk...")

    asn_stats = db.query(
        NetworkObservation.asn,
        func.count(func.distinct(NetworkObservation.src_ip)).label("ip_count"),
        func.count(func.distinct(NetworkObservation.geo_country)).label("country_count")
    ).filter(
        NetworkObservation.asn.isnot(None),
        NetworkObservation.asn != ""
    ).group_by(NetworkObservation.asn).all()

    if not asn_stats:
        logger.info("No network observations to resolve ASNs from.")
        return

    existing_asns = {asn.asn_number: asn for asn in db.query(ASNEntity).all()}
    new_asns = []

    for row in asn_stats:
        asn_num = row[0]
        ip_count = int(row[1] or 0)
        country_count = int(row[2] or 0)

        if asn_num in existing_asns:
            asn_ent = existing_asns[asn_num]
            asn_ent.ip_count = ip_count
            asn_ent.country_count = country_count
        else:
            asn_ent = ASNEntity(
                asn_number=asn_num,
                name=f"ASN {asn_num}",
                ip_count=ip_count,
                country_count=country_count,
                created_at=datetime.utcnow()
            )
            new_asns.append(asn_ent)

    if new_asns:
        for i in range(0, len(new_asns), 5000):
            db.bulk_save_objects(new_asns[i:i+5000])
            db.commit()
    else:
        db.commit()

    logger.info(f"ASN resolution complete: {len(asn_stats)} unique ASNs resolved.")


def resolve_all(db: Session):
    """Run full entity resolution pipeline with zero N+1 queries."""
    resolve_wallets(db)
    resolve_ips(db)
    resolve_asns(db)
