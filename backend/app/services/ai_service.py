"""
BTC-SHIELD AI Interpretation Service
MockAIProvider: Deterministic rule-based explainability.
Analyzes evidence items, generates structured explanations.
NEVER creates new entities, fabricated relationships, or unsupported evidence.
"""
from sqlalchemy.orm import Session
from app.models.models import Evidence, Alert, BehavioralFeature, AnomalyResult, Wallet
import logging

logger = logging.getLogger(__name__)


def get_interpretation(db: Session, entity_type: str, entity_id: str) -> dict:
    """
    Generate an AI interpretation for an entity based on available evidence.
    Uses MockAIProvider (deterministic, rule-based) — works offline without any API.
    """
    # Gather evidence
    evidences = db.query(Evidence).filter(
        Evidence.entity_type == entity_type,
        Evidence.entity_id == entity_id
    ).all()

    # Gather behavioral features
    bf = db.query(BehavioralFeature).filter(
        BehavioralFeature.entity_type == entity_type,
        BehavioralFeature.entity_id == entity_id
    ).first()

    # Gather alert info
    alert = db.query(Alert).filter(
        Alert.entity_type == entity_type,
        Alert.entity_id == entity_id
    ).first()

    # Gather anomaly result
    anomaly = db.query(AnomalyResult).filter(
        AnomalyResult.entity_type == entity_type,
        AnomalyResult.entity_id == entity_id
    ).order_by(AnomalyResult.created_at.desc()).first()

    features = bf.features if bf else {}

    # --- Build structured interpretation ---
    observations = []
    contributing_signals = []
    recommended_actions = []
    uncertainties = []
    insufficient_info = []

    if not evidences:
        return {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "summary": (
                f"No significant behavioral evidence has been generated for this {entity_type.lower()} entity. "
                f"The entity's behavioral profile falls within normal parameters based on available data."
            ),
            "observations": [],
            "contributing_signals": [],
            "recommended_review_actions": ["Continue monitoring for new activity"],
            "uncertainty": "High — insufficient evidence for meaningful assessment",
            "insufficient_information": ["No evidence signals generated from current data"],
            "confidence": 0.1,
        }

    # Categorize evidence
    categories_present = set()
    high_strength_signals = []
    for ev in evidences:
        categories_present.add(ev.category)
        observations.append(ev.observation)
        contributing_signals.append({
            "category": ev.category,
            "strength": round(ev.strength, 2),
            "evidence_id": ev.id,
        })
        if ev.strength > 0.7:
            high_strength_signals.append(ev)

    # --- Generate Summary ---
    summary_parts = []

    # Overall assessment
    if anomaly and anomaly.anomaly_score > 80:
        summary_parts.append(
            f"This {entity_type.lower()} exhibits strongly anomalous behavioral patterns "
            f"(anomaly score: {anomaly.anomaly_score:.1f}/100) as detected by the Isolation Forest model."
        )
    elif anomaly and anomaly.anomaly_score > 60:
        summary_parts.append(
            f"This {entity_type.lower()} shows moderately elevated anomaly indicators "
            f"(score: {anomaly.anomaly_score:.1f}/100)."
        )
    else:
        summary_parts.append(
            f"This {entity_type.lower()} has mild behavioral deviations detected."
        )

    # Evidence category analysis
    summary_parts.append(
        f"Analysis is supported by {len(evidences)} evidence signals across "
        f"{len(categories_present)} categories: {', '.join(sorted(categories_present))}."
    )

    # Specific pattern descriptions
    if "TEMPORAL" in categories_present:
        burstiness = features.get("burstiness", 0)
        if burstiness > 3:
            summary_parts.append(
                f"Temporal analysis reveals bursty transaction patterns "
                f"(burstiness coefficient: {burstiness:.2f}), suggesting automated "
                f"or coordinated activity windows rather than organic usage."
            )
        recommended_actions.append("Examine temporal clustering of transactions for coordination patterns")

    if "NETWORK" in categories_present or "GEOGRAPHIC" in categories_present:
        ip_count = features.get("unique_ip_count", 0)
        asn_count = features.get("unique_asn_count", 0)
        country_count = features.get("unique_country_count", 0)
        summary_parts.append(
            f"Network infrastructure analysis shows activity from {ip_count} unique IPs, "
            f"{asn_count} ASNs, and {country_count} countries, indicating "
            f"{'distributed operational infrastructure' if asn_count > 3 else 'moderate geographic spread'}."
        )
        recommended_actions.append("Investigate IP-to-wallet mapping for infrastructure analysis")
        if country_count > 3:
            recommended_actions.append("Check for impossible travel times between geographic observations")

    if "AMOUNT" in categories_present:
        summary_parts.append(
            "Transaction amount analysis reveals statistical anomalies in value distribution."
        )
        recommended_actions.append("Review individual transaction amounts for structuring patterns")

    if "TRANSACTION" in categories_present:
        fan_out = features.get("fan_out", 0)
        fan_in = features.get("fan_in", 0)
        if fan_out > 10:
            summary_parts.append(
                f"High fan-out pattern ({fan_out} outputs) may indicate peeling chain, "
                f"tumbling, or distribution behavior requiring further investigation."
            )
            recommended_actions.append("Trace output addresses for peeling chain or tumbling patterns")
        if fan_in > 10:
            summary_parts.append(
                f"High fan-in pattern ({fan_in} inputs) suggests consolidation or "
                f"aggregation behavior."
            )
            recommended_actions.append("Identify source wallets for consolidation analysis")

    if "CLUSTER" in categories_present:
        summary_parts.append(
            "DBSCAN clustering identified this entity as a behavioral outlier, "
            "not fitting any identified peer group in the dataset."
        )

    if "GRAPH" in categories_present:
        summary_parts.append(
            "Graph analysis indicates unusual counterparty interaction patterns."
        )
        recommended_actions.append("Explore graph neighborhood for related entities")

    # Default actions
    recommended_actions.extend([
        "Review transaction history chronologically",
        "Examine counterparty wallet relationships",
        "Cross-reference with any known investigation context",
    ])

    # Uncertainties
    if features.get("tx_count", 0) < 5:
        uncertainties.append("Limited transaction history may produce unreliable statistical features")
    if features.get("network_observation_count", 0) < 3:
        uncertainties.append("Limited network observations reduce confidence in infrastructure analysis")
    if not anomaly:
        uncertainties.append("No ML model score available — entity was not processed by anomaly detection")

    # Insufficient information
    if not features.get("unique_ip_count"):
        insufficient_info.append("No network observation data available for IP analysis")
    if features.get("unique_counterparties", 0) == 0:
        insufficient_info.append("No counterparty relationships resolved")

    # Confidence calculation
    if high_strength_signals and len(categories_present) >= 3:
        confidence = 0.85
    elif len(evidences) >= 3:
        confidence = 0.7
    elif len(evidences) >= 1:
        confidence = 0.5
    else:
        confidence = 0.2

    uncertainty_text = "; ".join(uncertainties) if uncertainties else "Low — sufficient evidence available for assessment"

    summary = " ".join(summary_parts)

    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "summary": summary,
        "observations": observations,
        "contributing_signals": contributing_signals,
        "recommended_review_actions": list(dict.fromkeys(recommended_actions)),  # deduplicate
        "uncertainty": uncertainty_text,
        "insufficient_information": insufficient_info if insufficient_info else ["None identified"],
        "confidence": round(confidence, 2),
        "evidence_count": len(evidences),
        "categories_analyzed": sorted(categories_present),
    }
