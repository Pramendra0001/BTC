"""
BTC-SHIELD Alert Prioritization Service
Generates ranked investigative leads from evidence and ML results.
Separates: Anomaly Score (model distance), Confidence (data sufficiency), Priority (compound rank).
"""
from sqlalchemy.orm import Session
from app.models.models import Alert, Evidence, AnomalyResult, BehavioralFeature, ModelRun
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def generate_alerts(db: Session):
    """
    Generate prioritized investigative alerts from evidence and anomaly results.
    
    Priority Calculation:
    - Anomaly Score: From Isolation Forest (mathematical distance from normal, 0-100)
    - Confidence: Data sufficiency score based on evidence count + feature completeness (0-1)
    - Priority: CRITICAL / HIGH / MEDIUM / LOW based on compound score
    """
    logger.info("Generating alerts...")

    # Clear old alerts
    db.query(Alert).delete()
    db.commit()

    # Get latest model run
    latest_model = db.query(ModelRun).filter(
        ModelRun.model_type == "IsolationForest",
        ModelRun.status == "COMPLETED"
    ).order_by(ModelRun.training_timestamp.desc()).first()

    model_version = latest_model.model_version if latest_model else "none"

    # Pre-fetch all anomaly scores in a single query
    anomaly_map = {
        (ar.entity_type, ar.entity_id): ar.anomaly_score
        for ar in db.query(AnomalyResult).filter(AnomalyResult.anomaly_score.isnot(None)).all()
    }

    # Group evidence by entity
    evidences = db.query(Evidence).all()
    entity_evidence_map: dict[tuple[str, str], list[Evidence]] = {}
    for ev in evidences:
        key = (ev.entity_type, ev.entity_id)
        if key not in entity_evidence_map:
            entity_evidence_map[key] = []
        entity_evidence_map[key].append(ev)

    alert_count = 0

    for (entity_type, entity_id), ev_list in entity_evidence_map.items():
        # --- Anomaly Score ---
        anomaly_score = anomaly_map.get((entity_type, entity_id), 0.0)

        # --- Confidence ---
        # Based on evidence quantity and diversity
        evidence_categories = set(ev.category for ev in ev_list)
        category_diversity = len(evidence_categories) / 8.0  # max 8 categories
        evidence_quantity = min(len(ev_list) / 5.0, 1.0)  # saturates at 5
        avg_strength = sum(ev.strength for ev in ev_list) / max(len(ev_list), 1)

        confidence = min(
            (category_diversity * 0.3 + evidence_quantity * 0.4 + avg_strength * 0.3),
            1.0
        )

        # --- Contributing Signals ---
        signals = []
        for ev in ev_list:
            signals.append({
                "category": ev.category,
                "observation": ev.observation[:120],
                "strength": round(ev.strength, 2),
                "evidence_id": ev.id,
            })

        # --- Priority ---
        compound_score = anomaly_score * 0.5 + confidence * 50 + avg_strength * 50

        if compound_score > 80:
            priority = "CRITICAL"
        elif compound_score > 60:
            priority = "HIGH"
        elif compound_score > 40:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        alert = Alert(
            entity_type=entity_type,
            entity_id=entity_id,
            priority=priority,
            anomaly_score=round(anomaly_score, 2),
            confidence=round(confidence, 3),
            model_version=model_version,
            contributing_signals=signals,
            evidence_ids=[ev.id for ev in ev_list],
            status="NEW",
            review_state="UNREVIEWED",
        )
        db.add(alert)
        alert_count += 1

    db.commit()

    # Log summary
    priorities = {}
    for alert in db.query(Alert).all():
        priorities[alert.priority] = priorities.get(alert.priority, 0) + 1

    logger.info(
        f"Alert generation complete: {alert_count} alerts created. "
        f"Distribution: {priorities}"
    )
    return alert_count
