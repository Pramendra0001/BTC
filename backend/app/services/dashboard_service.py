"""
BTC-SHIELD Dashboard Service
Aggregates real database counts for the command center.
All numbers from actual DB queries — ZERO hardcoded values.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.models import (
    Dataset, Transaction, Wallet, IPEntity, ASNEntity,
    Alert, Case, Evidence, ModelRun, AnomalyResult, NetworkObservation
)
import logging

logger = logging.getLogger(__name__)


def get_dashboard(db: Session) -> dict:
    """Aggregate dashboard statistics from real database state."""

    # Core counts
    total_datasets = db.query(Dataset).count()
    total_transactions = db.query(Transaction).count()
    total_wallets = db.query(Wallet).count()
    total_ips = db.query(IPEntity).count()
    total_asns = db.query(ASNEntity).count()
    total_observations = db.query(NetworkObservation).count()

    # Alert counts by priority
    alert_critical = db.query(Alert).filter(Alert.priority == "CRITICAL").count()
    alert_high = db.query(Alert).filter(Alert.priority == "HIGH").count()
    alert_medium = db.query(Alert).filter(Alert.priority == "MEDIUM").count()
    alert_low = db.query(Alert).filter(Alert.priority == "LOW").count()
    total_alerts = alert_critical + alert_high + alert_medium + alert_low

    # Alert counts by status
    alerts_new = db.query(Alert).filter(Alert.status == "NEW").count()
    alerts_reviewing = db.query(Alert).filter(Alert.status == "REVIEWING").count()
    alerts_resolved = db.query(Alert).filter(Alert.status == "RESOLVED").count()

    # Case counts
    cases_open = db.query(Case).filter(Case.status == "OPEN").count()
    cases_active = db.query(Case).filter(Case.status == "ACTIVE").count()
    cases_closed = db.query(Case).filter(Case.status == "CLOSED").count()
    total_cases = cases_open + cases_active + cases_closed

    # Evidence counts
    total_evidence = db.query(Evidence).count()

    # Model info
    total_model_runs = db.query(ModelRun).count()
    latest_model = db.query(ModelRun).order_by(
        ModelRun.training_timestamp.desc()
    ).first()

    # Anomaly score distribution (for chart)
    anomaly_distribution = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}
    anomaly_results = db.query(AnomalyResult).filter(
        AnomalyResult.anomaly_score.isnot(None)
    ).all()
    for ar in anomaly_results:
        score = ar.anomaly_score
        if score <= 20:
            anomaly_distribution["0-20"] += 1
        elif score <= 40:
            anomaly_distribution["20-40"] += 1
        elif score <= 60:
            anomaly_distribution["40-60"] += 1
        elif score <= 80:
            anomaly_distribution["60-80"] += 1
        else:
            anomaly_distribution["80-100"] += 1

    # Recent alerts
    recent_alerts = db.query(Alert).order_by(
        Alert.created_at.desc()
    ).limit(10).all()

    recent_alerts_list = [
        {
            "id": a.id,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "priority": a.priority,
            "anomaly_score": round(a.anomaly_score, 1) if a.anomaly_score else 0,
            "status": a.status,
            "created_at": a.created_at.isoformat() if a.created_at else None,
        }
        for a in recent_alerts
    ]

    # Dataset processing status
    datasets_pending = db.query(Dataset).filter(Dataset.status == "PENDING").count()
    datasets_processing = db.query(Dataset).filter(Dataset.status.in_(["PROCESSING", "PROCESSING_PIPELINE"])).count()
    datasets_completed = db.query(Dataset).filter(Dataset.status == "COMPLETED").count()
    datasets_failed = db.query(Dataset).filter(Dataset.status == "FAILED").count()

    return {
        "stats": {
            "totalTx": total_transactions,
            "activeWallets": total_wallets,
            "monitoredIps": total_ips,
            "activeAlerts": total_alerts,
            "totalAsns": total_asns,
            "totalObservations": total_observations,
            "openCases": total_cases,
            "totalEvidence": total_evidence,
            "totalDatasets": total_datasets,
        },
        "alerts": {
            "critical": alert_critical,
            "high": alert_high,
            "medium": alert_medium,
            "low": alert_low,
            "new": alerts_new,
            "reviewing": alerts_reviewing,
            "resolved": alerts_resolved,
        },
        "cases": {
            "open": cases_open,
            "active": cases_active,
            "closed": cases_closed,
        },
        "anomalyDistribution": anomaly_distribution,
        "recentAlerts": recent_alerts_list,
        "processingStatus": {
            "pending": datasets_pending,
            "processing": datasets_processing,
            "completed": datasets_completed,
            "failed": datasets_failed,
        },
        "modelInfo": {
            "totalRuns": total_model_runs,
            "latestModel": latest_model.model_version if latest_model else None,
            "latestTrainedAt": latest_model.training_timestamp.isoformat() if latest_model and latest_model.training_timestamp else None,
        },
    }
