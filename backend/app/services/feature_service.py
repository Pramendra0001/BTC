"""
BTC-SHIELD Feature Engineering Service
Computes behavioral features for entity anomaly detection.
Features: transaction, temporal, counterparty, network, graph-structural.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import (
    Wallet, Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, IPEntity, BehavioralFeature
)
from datetime import datetime
import numpy as np
import math
import logging

logger = logging.getLogger(__name__)

FEATURE_SCHEMA_VERSION = "2.0"


def _shannon_entropy(counts: list[int]) -> float:
    """Compute Shannon entropy of a distribution."""
    total = sum(counts)
    if total == 0:
        return 0.0
    probs = [c / total for c in counts if c > 0]
    return -sum(p * math.log2(p) for p in probs)


def _stats(values: list[float]) -> dict:
    """Compute basic statistics for a list of values."""
    if not values:
        return {"count": 0, "sum": 0, "mean": 0, "median": 0, "std": 0, "min": 0, "max": 0, "variance": 0}
    arr = np.array(values, dtype=float)
    return {
        "count": len(values),
        "sum": float(np.sum(arr)),
        "mean": float(np.mean(arr)),
        "median": float(np.median(arr)),
        "std": float(np.std(arr)),
        "min": float(np.min(arr)),
        "max": float(np.max(arr)),
        "variance": float(np.var(arr)),
    }


def compute_wallet_features(db: Session):
    """Compute comprehensive behavioral features for each wallet."""
    wallets = db.query(Wallet).all()
    logger.info(f"Computing features for {len(wallets)} wallets")

    for wallet in wallets:
        try:
            features = {}

            # --- Transaction Volume Features ---
            features["tx_count"] = wallet.tx_count or 0
            features["total_sent"] = wallet.total_sent or 0
            features["total_received"] = wallet.total_received or 0
            features["net_flow"] = (wallet.total_received or 0) - (wallet.total_sent or 0)
            features["avg_amount"] = ((wallet.total_sent or 0) + (wallet.total_received or 0)) / max(wallet.tx_count or 1, 1)

            # Get input transactions for this wallet
            inputs = db.query(TransactionInput).filter(
                TransactionInput.wallet_address == wallet.address
            ).all()
            outputs = db.query(TransactionOutput).filter(
                TransactionOutput.wallet_address == wallet.address
            ).all()

            input_amounts = [i.amount for i in inputs if i.amount]
            output_amounts = [o.amount for o in outputs if o.amount]
            all_amounts = input_amounts + output_amounts

            amount_stats = _stats(all_amounts)
            features["amount_mean"] = amount_stats["mean"]
            features["amount_median"] = amount_stats["median"]
            features["amount_std"] = amount_stats["std"]
            features["amount_variance"] = amount_stats["variance"]
            features["amount_min"] = amount_stats["min"]
            features["amount_max"] = amount_stats["max"]

            # --- Fan-in / Fan-out ---
            features["fan_in"] = len(inputs)
            features["fan_out"] = len(outputs)
            features["fan_ratio"] = features["fan_out"] / max(features["fan_in"], 1)

            # --- Fee Statistics ---
            tx_ids_in = [i.transaction_id for i in inputs]
            tx_ids_out = [o.transaction_id for o in outputs]
            all_tx_ids = list(set(tx_ids_in + tx_ids_out))

            if all_tx_ids:
                txs = db.query(Transaction).filter(Transaction.id.in_(all_tx_ids)).all()
                fees = [t.fee for t in txs if t.fee is not None and t.fee > 0]
                fee_stats = _stats(fees)
                features["fee_mean"] = fee_stats["mean"]
                features["fee_std"] = fee_stats["std"]
                features["fee_max"] = fee_stats["max"]

                # Fee-to-value ratio
                total_val = sum(all_amounts) if all_amounts else 0
                features["fee_to_value_ratio"] = sum(fees) / max(total_val, 1) if fees else 0

                # --- Temporal Features ---
                timestamps = sorted([t.timestamp for t in txs if t.timestamp])
                if len(timestamps) >= 2:
                    deltas = [(timestamps[i+1] - timestamps[i]).total_seconds()
                              for i in range(len(timestamps) - 1)]
                    delta_stats = _stats(deltas)
                    features["tx_velocity"] = len(timestamps)  # total tx count
                    features["inter_arrival_mean"] = delta_stats["mean"]
                    features["inter_arrival_std"] = delta_stats["std"]
                    features["inter_arrival_min"] = delta_stats["min"]

                    # Burstiness: coefficient of variation of inter-arrival times
                    features["burstiness"] = delta_stats["std"] / max(delta_stats["mean"], 0.001)

                    # Time span
                    total_span = (timestamps[-1] - timestamps[0]).total_seconds()
                    features["active_duration_hours"] = total_span / 3600

                    # Hour-of-day distribution
                    hours = [t.hour for t in timestamps]
                    hour_counts = [hours.count(h) for h in range(24)]
                    features["hour_entropy"] = _shannon_entropy(hour_counts)
                    features["peak_hour"] = hours[0] if hours else 0
                else:
                    features["tx_velocity"] = len(timestamps)
                    features["inter_arrival_mean"] = 0
                    features["inter_arrival_std"] = 0
                    features["inter_arrival_min"] = 0
                    features["burstiness"] = 0
                    features["active_duration_hours"] = 0
                    features["hour_entropy"] = 0
                    features["peak_hour"] = 0
            else:
                features.update({
                    "fee_mean": 0, "fee_std": 0, "fee_max": 0, "fee_to_value_ratio": 0,
                    "tx_velocity": 0, "inter_arrival_mean": 0, "inter_arrival_std": 0,
                    "inter_arrival_min": 0, "burstiness": 0, "active_duration_hours": 0,
                    "hour_entropy": 0, "peak_hour": 0,
                })

            # --- Counterparty Features ---
            counterparty_addrs_in = set()
            for inp in inputs:
                # Find outputs of same transaction (counterparties)
                tx_outputs = db.query(TransactionOutput).filter(
                    TransactionOutput.transaction_id == inp.transaction_id,
                    TransactionOutput.wallet_address != wallet.address
                ).all()
                for o in tx_outputs:
                    counterparty_addrs_in.add(o.wallet_address)

            counterparty_addrs_out = set()
            for out in outputs:
                tx_inputs = db.query(TransactionInput).filter(
                    TransactionInput.transaction_id == out.transaction_id,
                    TransactionInput.wallet_address != wallet.address
                ).all()
                for inp in tx_inputs:
                    counterparty_addrs_out.add(inp.wallet_address)

            all_counterparties = counterparty_addrs_in | counterparty_addrs_out
            features["unique_counterparties"] = len(all_counterparties)
            features["counterparty_in_count"] = len(counterparty_addrs_in)
            features["counterparty_out_count"] = len(counterparty_addrs_out)

            # Counterparty concentration (how concentrated are interactions)
            if all_counterparties and all_tx_ids:
                cp_counts = []
                for cp in all_counterparties:
                    count = db.query(TransactionInput).filter(
                        TransactionInput.wallet_address == cp,
                        TransactionInput.transaction_id.in_(all_tx_ids)
                    ).count() + db.query(TransactionOutput).filter(
                        TransactionOutput.wallet_address == cp,
                        TransactionOutput.transaction_id.in_(all_tx_ids)
                    ).count()
                    cp_counts.append(count)
                features["counterparty_entropy"] = _shannon_entropy(cp_counts)
            else:
                features["counterparty_entropy"] = 0

            # --- Network Features ---
            net_obs = db.query(NetworkObservation).filter(
                NetworkObservation.transaction_id.in_(
                    [t.txid for t in db.query(Transaction).filter(Transaction.id.in_(all_tx_ids)).all()]
                    if all_tx_ids else []
                )
            ).all() if all_tx_ids else []

            unique_ips = set(o.src_ip for o in net_obs if o.src_ip)
            unique_asns = set(o.asn for o in net_obs if o.asn)
            unique_countries = set(o.geo_country for o in net_obs if o.geo_country)

            features["unique_ip_count"] = len(unique_ips)
            features["unique_asn_count"] = len(unique_asns)
            features["unique_country_count"] = len(unique_countries)
            features["network_observation_count"] = len(net_obs)

            # ASN diversity
            if net_obs:
                asn_list = [o.asn for o in net_obs if o.asn]
                asn_counts = [asn_list.count(a) for a in set(asn_list)]
                features["asn_entropy"] = _shannon_entropy(asn_counts) if asn_counts else 0
            else:
                features["asn_entropy"] = 0

            # --- Save features ---
            bf = db.query(BehavioralFeature).filter(
                BehavioralFeature.entity_type == "WALLET",
                BehavioralFeature.entity_id == wallet.address
            ).first()

            if not bf:
                bf = BehavioralFeature(
                    entity_type="WALLET",
                    entity_id=wallet.address,
                    feature_schema_version=FEATURE_SCHEMA_VERSION
                )
                db.add(bf)

            bf.features = features
            bf.feature_schema_version = FEATURE_SCHEMA_VERSION
            bf.computed_at = datetime.utcnow()

        except Exception as e:
            logger.warning(f"Error computing features for wallet {wallet.address}: {e}")
            continue

    db.commit()
    logger.info("Wallet feature computation complete")


def compute_ip_features(db: Session):
    """Compute behavioral features for IP entities."""
    ips = db.query(IPEntity).all()
    logger.info(f"Computing features for {len(ips)} IPs")

    for ip_ent in ips:
        try:
            observations = db.query(NetworkObservation).filter(
                NetworkObservation.src_ip == ip_ent.ip_address
            ).all()

            features = {
                "observation_count": len(observations),
                "unique_txids": len(set(o.transaction_id for o in observations if o.transaction_id)),
                "unique_dst_ips": len(set(o.dst_ip for o in observations if o.dst_ip)),
                "unique_countries": len(set(o.geo_country for o in observations if o.geo_country)),
                "asn": ip_ent.asn or "",
                "country": ip_ent.country or "",
            }

            # Temporal features
            timestamps = sorted([o.timestamp for o in observations if o.timestamp])
            if len(timestamps) >= 2:
                deltas = [(timestamps[i+1] - timestamps[i]).total_seconds()
                          for i in range(len(timestamps) - 1)]
                features["inter_obs_mean"] = float(np.mean(deltas))
                features["inter_obs_std"] = float(np.std(deltas))
                features["active_hours"] = (timestamps[-1] - timestamps[0]).total_seconds() / 3600
            else:
                features["inter_obs_mean"] = 0
                features["inter_obs_std"] = 0
                features["active_hours"] = 0

            # Related wallets
            related_txids = set(o.transaction_id for o in observations if o.transaction_id)
            if related_txids:
                related_txs = db.query(Transaction).filter(Transaction.txid.in_(related_txids)).all()
                related_tx_ids = [t.id for t in related_txs]
                if related_tx_ids:
                    wallet_addrs = set()
                    for tid in related_tx_ids:
                        ins = db.query(TransactionInput).filter(TransactionInput.transaction_id == tid).all()
                        outs = db.query(TransactionOutput).filter(TransactionOutput.transaction_id == tid).all()
                        wallet_addrs.update(i.wallet_address for i in ins if i.wallet_address)
                        wallet_addrs.update(o.wallet_address for o in outs if o.wallet_address)
                    features["unique_wallet_count"] = len(wallet_addrs)
                else:
                    features["unique_wallet_count"] = 0
            else:
                features["unique_wallet_count"] = 0

            bf = db.query(BehavioralFeature).filter(
                BehavioralFeature.entity_type == "IP",
                BehavioralFeature.entity_id == ip_ent.ip_address
            ).first()
            if not bf:
                bf = BehavioralFeature(
                    entity_type="IP",
                    entity_id=ip_ent.ip_address,
                    feature_schema_version=FEATURE_SCHEMA_VERSION
                )
                db.add(bf)
            bf.features = features
            bf.computed_at = datetime.utcnow()

        except Exception as e:
            logger.warning(f"Error computing IP features for {ip_ent.ip_address}: {e}")

    db.commit()
    logger.info("IP feature computation complete")


def compute_all_features(db: Session):
    """Compute all behavioral features."""
    compute_wallet_features(db)
    compute_ip_features(db)
