"""
BTC-SHIELD Feature Engineering Service
Computes behavioral features for entity anomaly detection.
Features: transaction, temporal, counterparty, network, graph-structural.
Optimized with bulk pre-fetching for instant O(1) in-memory computation.
"""
from sqlalchemy.orm import Session
from collections import defaultdict
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
    """Compute comprehensive behavioral features for each wallet in bulk."""
    wallets = db.query(Wallet).all()
    if not wallets:
        return

    logger.info(f"Preloading entities for {len(wallets)} wallets...")

    # Pre-fetch all inputs, outputs, transactions, and observations in 4 queries
    all_inputs = db.query(TransactionInput).all()
    all_outputs = db.query(TransactionOutput).all()
    all_txs = db.query(Transaction).all()
    all_obs = db.query(NetworkObservation).all()

    # Pre-index into memory maps
    tx_map = {t.id: t for t in all_txs}
    txid_to_tx_map = {t.txid: t for t in all_txs}

    inputs_by_wallet = defaultdict(list)
    outputs_by_wallet = defaultdict(list)
    inputs_by_tx = defaultdict(list)
    outputs_by_tx = defaultdict(list)

    for inp in all_inputs:
        inputs_by_wallet[inp.wallet_address].append(inp)
        inputs_by_tx[inp.transaction_id].append(inp)

    for out in all_outputs:
        outputs_by_wallet[out.wallet_address].append(out)
        outputs_by_tx[out.transaction_id].append(out)

    obs_by_txid = defaultdict(list)
    for o in all_obs:
        if o.transaction_id:
            obs_by_txid[o.transaction_id].append(o)

    # Existing behavioral features map to update or create
    existing_bf = {
        bf.entity_id: bf
        for bf in db.query(BehavioralFeature).filter(BehavioralFeature.entity_type == "WALLET").all()
    }

    logger.info(f"Computing behavioral features in-memory for {len(wallets)} wallets...")

    for wallet in wallets:
        try:
            features = {}
            w_inputs = inputs_by_wallet.get(wallet.address, [])
            w_outputs = outputs_by_wallet.get(wallet.address, [])

            # --- Transaction Volume Features ---
            features["tx_count"] = wallet.tx_count or 0
            features["total_sent"] = wallet.total_sent or 0
            features["total_received"] = wallet.total_received or 0
            features["net_flow"] = (wallet.total_received or 0) - (wallet.total_sent or 0)
            features["avg_amount"] = (
                ((wallet.total_sent or 0) + (wallet.total_received or 0)) / max(wallet.tx_count or 1, 1)
            )

            input_amounts = [i.amount for i in w_inputs if i.amount]
            output_amounts = [o.amount for o in w_outputs if o.amount]
            all_amounts = input_amounts + output_amounts

            amount_stats = _stats(all_amounts)
            features["amount_mean"] = amount_stats["mean"]
            features["amount_median"] = amount_stats["median"]
            features["amount_std"] = amount_stats["std"]
            features["amount_variance"] = amount_stats["variance"]
            features["amount_min"] = amount_stats["min"]
            features["amount_max"] = amount_stats["max"]

            # --- Fan-in / Fan-out ---
            features["fan_in"] = len(w_inputs)
            features["fan_out"] = len(w_outputs)
            features["fan_ratio"] = features["fan_out"] / max(features["fan_in"], 1)

            # --- Fee Statistics ---
            tx_ids_in = [i.transaction_id for i in w_inputs]
            tx_ids_out = [o.transaction_id for o in w_outputs]
            all_tx_ids = list(set(tx_ids_in + tx_ids_out))

            wallet_txs = [tx_map[tid] for tid in all_tx_ids if tid in tx_map]

            if wallet_txs:
                fees = [t.fee for t in wallet_txs if t.fee is not None and t.fee > 0]
                fee_stats = _stats(fees)
                features["fee_mean"] = fee_stats["mean"]
                features["fee_std"] = fee_stats["std"]
                features["fee_max"] = fee_stats["max"]

                total_val = sum(all_amounts) if all_amounts else 0
                features["fee_to_value_ratio"] = sum(fees) / max(total_val, 1) if fees else 0

                # --- Temporal Features ---
                timestamps = sorted([t.timestamp for t in wallet_txs if t.timestamp])
                if len(timestamps) >= 2:
                    deltas = [(timestamps[i+1] - timestamps[i]).total_seconds()
                              for i in range(len(timestamps) - 1)]
                    delta_stats = _stats(deltas)
                    features["tx_velocity"] = len(timestamps)
                    features["inter_arrival_mean"] = delta_stats["mean"]
                    features["inter_arrival_std"] = delta_stats["std"]
                    features["inter_arrival_min"] = delta_stats["min"]
                    features["burstiness"] = delta_stats["std"] / max(delta_stats["mean"], 0.001)

                    total_span = (timestamps[-1] - timestamps[0]).total_seconds()
                    features["active_duration_hours"] = total_span / 3600

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
            for inp in w_inputs:
                tx_outs = outputs_by_tx.get(inp.transaction_id, [])
                for o in tx_outs:
                    if o.wallet_address != wallet.address:
                        counterparty_addrs_in.add(o.wallet_address)

            counterparty_addrs_out = set()
            for out in w_outputs:
                tx_ins = inputs_by_tx.get(out.transaction_id, [])
                for i in tx_ins:
                    if i.wallet_address != wallet.address:
                        counterparty_addrs_out.add(i.wallet_address)

            all_counterparties = counterparty_addrs_in | counterparty_addrs_out
            features["unique_counterparties"] = len(all_counterparties)
            features["counterparty_in_count"] = len(counterparty_addrs_in)
            features["counterparty_out_count"] = len(counterparty_addrs_out)

            # Counterparty distribution
            if all_counterparties and all_tx_ids:
                tx_id_set = set(all_tx_ids)
                cp_counts = []
                for cp in all_counterparties:
                    c_in = sum(1 for inp in inputs_by_wallet.get(cp, []) if inp.transaction_id in tx_id_set)
                    c_out = sum(1 for out in outputs_by_wallet.get(cp, []) if out.transaction_id in tx_id_set)
                    cp_counts.append(c_in + c_out)
                features["counterparty_entropy"] = _shannon_entropy(cp_counts)
            else:
                features["counterparty_entropy"] = 0

            # --- Network Features ---
            net_obs = []
            for t in wallet_txs:
                if t.txid in obs_by_txid:
                    net_obs.extend(obs_by_txid[t.txid])

            unique_ips = set(o.src_ip for o in net_obs if o.src_ip)
            unique_asns = set(o.asn for o in net_obs if o.asn)
            unique_countries = set(o.geo_country for o in net_obs if o.geo_country)

            features["unique_ip_count"] = len(unique_ips)
            features["unique_asn_count"] = len(unique_asns)
            features["unique_country_count"] = len(unique_countries)
            features["network_observation_count"] = len(net_obs)

            if net_obs:
                asn_list = [o.asn for o in net_obs if o.asn]
                asn_counts = [asn_list.count(a) for a in set(asn_list)]
                features["asn_entropy"] = _shannon_entropy(asn_counts) if asn_counts else 0
            else:
                features["asn_entropy"] = 0

            # --- Save features ---
            bf = existing_bf.get(wallet.address)
            if not bf:
                bf = BehavioralFeature(
                    entity_type="WALLET",
                    entity_id=wallet.address,
                    feature_schema_version=FEATURE_SCHEMA_VERSION
                )
                db.add(bf)
                existing_bf[wallet.address] = bf

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
    if not ips:
        return

    logger.info(f"Computing features for {len(ips)} IPs...")

    all_obs = db.query(NetworkObservation).all()
    obs_by_ip = defaultdict(list)
    for o in all_obs:
        obs_by_ip[o.src_ip].append(o)

    existing_bf = {
        bf.entity_id: bf
        for bf in db.query(BehavioralFeature).filter(BehavioralFeature.entity_type == "IP").all()
    }

    for ip_ent in ips:
        try:
            observations = obs_by_ip.get(ip_ent.ip_address, [])

            features = {
                "observation_count": len(observations),
                "unique_txids": len(set(o.transaction_id for o in observations if o.transaction_id)),
                "unique_dst_ips": len(set(o.dst_ip for o in observations if o.dst_ip)),
                "unique_countries": len(set(o.geo_country for o in observations if o.geo_country)),
                "asn": ip_ent.asn or "",
                "country": ip_ent.country or "",
            }

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

            bf = existing_bf.get(ip_ent.ip_address)
            if not bf:
                bf = BehavioralFeature(
                    entity_type="IP",
                    entity_id=ip_ent.ip_address,
                    feature_schema_version=FEATURE_SCHEMA_VERSION
                )
                db.add(bf)
                existing_bf[ip_ent.ip_address] = bf

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
