"""
BTC-SHIELD Evidence Engine
Generates traceable evidence signals from features, ML results, and graph analysis.
Each evidence is linked to source data — never fabricated.
"""
from sqlalchemy.orm import Session
from app.models.models import (
    Evidence, AnomalyResult, BehavioralFeature, Wallet,
    Transaction, NetworkObservation, IPEntity
)
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_evidence(db: Session):
    """
    Generate evidence from:
    1. ML anomaly scores (MODEL category)
    2. Behavioral feature analysis (TRANSACTION, TEMPORAL, AMOUNT, NETWORK, GEOGRAPHIC)
    3. Graph-structural signals (GRAPH)
    """
    logger.info("Generating evidence...")

    # Clear old evidence to regenerate
    db.query(Evidence).delete()
    db.commit()

    evidence_count = 0

    # --- MODEL evidence: from Isolation Forest results ---
    anomalies = db.query(AnomalyResult).filter(
        AnomalyResult.anomaly_score > 60
    ).all()

    for a in anomalies:
        severity = "high" if a.anomaly_score > 80 else "moderate"
        ev = Evidence(
            entity_type=a.entity_type,
            entity_id=a.entity_id,
            category="MODEL",
            observation=(
                f"Isolation Forest detected {severity} behavioral anomaly "
                f"with score {a.anomaly_score:.1f}/100. Entity deviates significantly "
                f"from the baseline behavioral distribution."
            ),
            details={
                "anomaly_score": round(a.anomaly_score, 2),
                "model_run_id": a.model_run_id,
                "severity": severity,
            },
            strength=min(a.anomaly_score / 100.0, 1.0),
        )
        db.add(ev)
        evidence_count += 1

    # --- CLUSTER evidence: noise points from DBSCAN ---
    cluster_noise = db.query(AnomalyResult).filter(
        AnomalyResult.cluster_id == -1
    ).all()
    for cn in cluster_noise:
        ev = Evidence(
            entity_type=cn.entity_type,
            entity_id=cn.entity_id,
            category="CLUSTER",
            observation=(
                "Entity classified as behavioral outlier by DBSCAN clustering. "
                "Behavioral pattern does not fit any identified peer group."
            ),
            details={
                "cluster_id": -1,
                "model_run_id": cn.model_run_id,
            },
            strength=0.6,
        )
        db.add(ev)
        evidence_count += 1

    # --- BEHAVIORAL evidence from features ---
    features = db.query(BehavioralFeature).filter(
        BehavioralFeature.entity_type == "WALLET"
    ).all()

    for bf in features:
        f = bf.features or {}

        # AMOUNT anomaly: very high variance or extreme values
        if f.get("amount_variance", 0) > 0:
            cv = f.get("amount_std", 0) / max(f.get("amount_mean", 1), 1)
            if cv > 3.0:
                ev = Evidence(
                    entity_type="WALLET",
                    entity_id=bf.entity_id,
                    category="AMOUNT",
                    observation=(
                        f"Highly variable transaction amounts detected. "
                        f"Coefficient of variation: {cv:.2f} (mean: {f['amount_mean']:.0f}, "
                        f"std: {f['amount_std']:.0f}). May indicate structured payments "
                        f"or irregular financial behavior."
                    ),
                    details={
                        "coefficient_of_variation": round(cv, 2),
                        "amount_mean": f.get("amount_mean"),
                        "amount_std": f.get("amount_std"),
                        "amount_min": f.get("amount_min"),
                        "amount_max": f.get("amount_max"),
                    },
                    strength=min(cv / 5.0, 0.9),
                )
                db.add(ev)
                evidence_count += 1

        # TRANSACTION volume anomaly: very high tx count
        if f.get("tx_count", 0) > 20:
            ev = Evidence(
                entity_type="WALLET",
                entity_id=bf.entity_id,
                category="TRANSACTION",
                observation=(
                    f"Elevated transaction volume: {f['tx_count']} transactions observed. "
                    f"Total sent: {f.get('total_sent', 0):.0f}, "
                    f"Total received: {f.get('total_received', 0):.0f}."
                ),
                details={
                    "tx_count": f["tx_count"],
                    "total_sent": f.get("total_sent"),
                    "total_received": f.get("total_received"),
                },
                strength=min(f["tx_count"] / 50.0, 0.8),
            )
            db.add(ev)
            evidence_count += 1

        # FAN-OUT anomaly
        if f.get("fan_out", 0) > 10:
            ev = Evidence(
                entity_type="WALLET",
                entity_id=bf.entity_id,
                category="TRANSACTION",
                observation=(
                    f"High fan-out pattern detected: {f['fan_out']} output positions. "
                    f"Fan-in: {f.get('fan_in', 0)}, Ratio: {f.get('fan_ratio', 0):.2f}. "
                    f"May indicate peeling chain, tumbling, or distribution activity."
                ),
                details={
                    "fan_out": f["fan_out"],
                    "fan_in": f.get("fan_in"),
                    "fan_ratio": f.get("fan_ratio"),
                },
                strength=min(f["fan_out"] / 30.0, 0.85),
            )
            db.add(ev)
            evidence_count += 1

        # FAN-IN anomaly (consolidation)
        if f.get("fan_in", 0) > 10:
            ev = Evidence(
                entity_type="WALLET",
                entity_id=bf.entity_id,
                category="TRANSACTION",
                observation=(
                    f"High fan-in pattern detected: {f['fan_in']} input positions. "
                    f"May indicate consolidation or aggregation activity."
                ),
                details={"fan_in": f["fan_in"], "fan_out": f.get("fan_out")},
                strength=min(f["fan_in"] / 30.0, 0.8),
            )
            db.add(ev)
            evidence_count += 1

        # TEMPORAL anomaly: burstiness
        if f.get("burstiness", 0) > 3.0:
            ev = Evidence(
                entity_type="WALLET",
                entity_id=bf.entity_id,
                category="TEMPORAL",
                observation=(
                    f"Highly bursty transaction pattern. Burstiness coefficient: "
                    f"{f['burstiness']:.2f}. Mean inter-arrival time: "
                    f"{f.get('inter_arrival_mean', 0):.1f}s with std: "
                    f"{f.get('inter_arrival_std', 0):.1f}s. Suggests automated or "
                    f"coordinated activity windows."
                ),
                details={
                    "burstiness": f["burstiness"],
                    "inter_arrival_mean": f.get("inter_arrival_mean"),
                    "inter_arrival_std": f.get("inter_arrival_std"),
                },
                strength=min(f["burstiness"] / 5.0, 0.85),
            )
            db.add(ev)
            evidence_count += 1

        # FEE anomaly
        if f.get("fee_to_value_ratio", 0) > 0.05:
            ev = Evidence(
                entity_type="WALLET",
                entity_id=bf.entity_id,
                category="AMOUNT",
                observation=(
                    f"Unusual fee-to-value ratio: {f['fee_to_value_ratio']:.4f}. "
                    f"Abnormally high fees relative to transaction value may indicate "
                    f"urgency, priority manipulation, or fee-bumping behavior."
                ),
                details={
                    "fee_to_value_ratio": f["fee_to_value_ratio"],
                    "fee_mean": f.get("fee_mean"),
                },
                strength=min(f["fee_to_value_ratio"] * 5, 0.8),
            )
            db.add(ev)
            evidence_count += 1

        # NETWORK anomaly: multi-ASN or multi-country
        if f.get("unique_asn_count", 0) > 3:
            ev = Evidence(
                entity_type="WALLET",
                entity_id=bf.entity_id,
                category="NETWORK",
                observation=(
                    f"Transactions observed from {f['unique_asn_count']} distinct ASNs "
                    f"and {f.get('unique_ip_count', 0)} unique IPs across "
                    f"{f.get('unique_country_count', 0)} countries. "
                    f"Multi-infrastructure usage may indicate operational security "
                    f"measures or distributed infrastructure."
                ),
                details={
                    "unique_asn_count": f["unique_asn_count"],
                    "unique_ip_count": f.get("unique_ip_count"),
                    "unique_country_count": f.get("unique_country_count"),
                    "asn_entropy": f.get("asn_entropy"),
                },
                strength=min(f["unique_asn_count"] / 8.0, 0.9),
            )
            db.add(ev)
            evidence_count += 1

        # GEOGRAPHIC anomaly
        if f.get("unique_country_count", 0) > 3:
            ev = Evidence(
                entity_type="WALLET",
                entity_id=bf.entity_id,
                category="GEOGRAPHIC",
                observation=(
                    f"Wallet observed across {f['unique_country_count']} distinct countries. "
                    f"Geographic diversity suggests multi-jurisdictional operations "
                    f"or VPN/proxy usage."
                ),
                details={
                    "unique_country_count": f["unique_country_count"],
                    "unique_asn_count": f.get("unique_asn_count"),
                },
                strength=min(f["unique_country_count"] / 6.0, 0.85),
            )
            db.add(ev)
            evidence_count += 1

        # Low counterparty entropy (highly concentrated interactions)
        if f.get("unique_counterparties", 0) > 0 and f.get("counterparty_entropy", 0) < 1.0 and f.get("tx_count", 0) > 5:
            ev = Evidence(
                entity_type="WALLET",
                entity_id=bf.entity_id,
                category="GRAPH",
                observation=(
                    f"Low counterparty diversity. Entropy: {f['counterparty_entropy']:.2f}. "
                    f"Interactions highly concentrated among {f['unique_counterparties']} "
                    f"counterparties over {f['tx_count']} transactions."
                ),
                details={
                    "counterparty_entropy": f["counterparty_entropy"],
                    "unique_counterparties": f["unique_counterparties"],
                    "tx_count": f["tx_count"],
                },
                strength=max(0.3, 1.0 - f["counterparty_entropy"]),
            )
            db.add(ev)
            evidence_count += 1

    # --- STRUCTURAL HEURISTICS: Mixing / CoinJoin & Peeling Chains ---
    try:
        from app.services.heuristics_service import detect_mixing_patterns, detect_peeling_chains
        mix_patterns = detect_mixing_patterns(db, limit=50)
        for m in mix_patterns:
            ev = Evidence(
                entity_type="TRANSACTION",
                entity_id=m["txid"],
                category="GRAPH",
                observation=(
                    f"Structural pattern detected: {m['pattern_type']}. "
                    f"Transaction exhibits {m['output_count']} outputs with {m['max_equal_outputs']} "
                    f"identical denomination values ({m['entropy_bits']} bits entropy), "
                    f"matching CoinJoin/tumbler mixing heuristics."
                ),
                details=m,
                strength=min(1.0, m["confidence_score"] / 100.0)
            )
            db.add(ev)
            evidence_count += 1

        peel_chains = detect_peeling_chains(db, min_hops=2, limit=50)
        for pc in peel_chains:
            ev = Evidence(
                entity_type="TRANSACTION",
                entity_id=pc["start_txid"],
                category="GRAPH",
                observation=(
                    f"Peeling-chain cascade detected across {pc['hop_count']} sequential hops. "
                    f"Total peeled volume: {pc['total_peeled_btc']} BTC with change advancing to {pc['final_change_btc']} BTC."
                ),
                details=pc,
                strength=min(1.0, pc["confidence_score"] / 100.0)
            )
            db.add(ev)
            evidence_count += 1
    except Exception as e:
        logger.warning(f"Error generating heuristic evidence: {e}")

    db.commit()
    logger.info(f"Evidence generation complete: {evidence_count} evidence items created")
    return evidence_count
