"""
BTC-SHIELD Entity Resolution Service
Re-resolves and updates entity statistics from existing data.
Primary entity creation happens during ingestion; this service handles
post-ingestion re-computation and ASN entity aggregation.
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
    """Re-compute wallet aggregate statistics from transaction data."""
    wallets = db.query(Wallet).all()
    logger.info(f"Re-resolving {len(wallets)} wallets")

    for w in wallets:
        inputs = db.query(TransactionInput).filter(
            TransactionInput.wallet_address == w.address
        ).all()
        outputs = db.query(TransactionOutput).filter(
            TransactionOutput.wallet_address == w.address
        ).all()

        total_sent = sum(i.amount or 0 for i in inputs)
        total_received = sum(o.amount or 0 for o in outputs)
        tx_ids = set(i.transaction_id for i in inputs) | set(o.transaction_id for o in outputs)

        w.total_sent = total_sent
        w.total_received = total_received
        w.tx_count = len(tx_ids)

        # Update first/last seen from transactions
        if tx_ids:
            txs = db.query(Transaction).filter(Transaction.id.in_(tx_ids)).all()
            timestamps = [t.timestamp for t in txs if t.timestamp]
            if timestamps:
                w.first_seen = min(timestamps)
                w.last_seen = max(timestamps)

    db.commit()
    logger.info("Wallet re-resolution complete")


def resolve_ips(db: Session):
    """Re-compute IP entity statistics from network observations."""
    ips = db.query(IPEntity).all()
    logger.info(f"Re-resolving {len(ips)} IP entities")

    for ip_ent in ips:
        obs = db.query(NetworkObservation).filter(
            NetworkObservation.src_ip == ip_ent.ip_address
        ).all()

        ip_ent.observation_count = len(obs)

        timestamps = [o.timestamp for o in obs if o.timestamp]
        if timestamps:
            ip_ent.first_seen = min(timestamps)
            ip_ent.last_seen = max(timestamps)

        # Get most common ASN and country
        asns = [o.asn for o in obs if o.asn]
        countries = [o.geo_country for o in obs if o.geo_country]
        if asns:
            ip_ent.asn = max(set(asns), key=asns.count)
        if countries:
            ip_ent.country = max(set(countries), key=countries.count)

    db.commit()
    logger.info("IP re-resolution complete")


def resolve_asns(db: Session):
    """Re-compute ASN entity statistics."""
    asns = db.query(ASNEntity).all()
    logger.info(f"Re-resolving {len(asns)} ASN entities")

    for asn_ent in asns:
        # Count unique IPs for this ASN
        ip_count = db.query(IPEntity).filter(
            IPEntity.asn == asn_ent.asn_number
        ).count()
        asn_ent.ip_count = ip_count

        # Count unique countries
        countries = db.query(NetworkObservation.geo_country).filter(
            NetworkObservation.asn == asn_ent.asn_number,
            NetworkObservation.geo_country.isnot(None)
        ).distinct().count()
        asn_ent.country_count = countries

    db.commit()
    logger.info("ASN re-resolution complete")


def resolve_all(db: Session):
    """Run full entity resolution pipeline."""
    resolve_wallets(db)
    resolve_ips(db)
    resolve_asns(db)
