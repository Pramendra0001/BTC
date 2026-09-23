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
    """Aggregate dashboard statistics from real database state via unified SQL aggregations."""
    from sqlalchemy import case

    # Core table counts via direct primary key scalar count (avoids subquery overhead)
    total_transactions = db.query(func.count(Transaction.id)).scalar() or 0
    total_wallets = db.query(func.count(Wallet.id)).scalar() or 0
    total_ips = db.query(func.count(IPEntity.id)).scalar() or 0
    total_asns = db.query(func.count(ASNEntity.id)).scalar() or 0
    total_observations = db.query(func.count(NetworkObservation.id)).scalar() or 0
    total_evidence = db.query(func.count(Evidence.id)).scalar() or 0

    # Unified Alert counts (priority + status in a single SQL aggregation pass)
    alert_agg = db.query(
        func.count(case((Alert.priority == "CRITICAL", 1))),
        func.count(case((Alert.priority == "HIGH", 1))),
        func.count(case((Alert.priority == "MEDIUM", 1))),
        func.count(case((Alert.priority == "LOW", 1))),
        func.count(case((Alert.status == "NEW", 1))),
        func.count(case((Alert.status == "REVIEWING", 1))),
        func.count(case((Alert.status == "RESOLVED", 1))),
    ).first()

    if alert_agg:
        alert_critical = alert_agg[0] or 0
        alert_high = alert_agg[1] or 0
        alert_medium = alert_agg[2] or 0
        alert_low = alert_agg[3] or 0
        alerts_new = alert_agg[4] or 0
        alerts_reviewing = alert_agg[5] or 0
        alerts_resolved = alert_agg[6] or 0
    else:
        alert_critical = alert_high = alert_medium = alert_low = 0
        alerts_new = alerts_reviewing = alerts_resolved = 0

    total_alerts = alert_critical + alert_high + alert_medium + alert_low

    # Unified Case counts in a single query
    case_agg = db.query(
        func.count(case((Case.status == "OPEN", 1))),
        func.count(case((Case.status == "ACTIVE", 1))),
        func.count(case((Case.status == "CLOSED", 1))),
    ).first()

    cases_open = (case_agg[0] or 0) if case_agg else 0
    cases_active = (case_agg[1] or 0) if case_agg else 0
    cases_closed = (case_agg[2] or 0) if case_agg else 0
    total_cases = cases_open + cases_active + cases_closed

    # Unified Dataset counts in a single query
    ds_agg = db.query(
        func.count(case((Dataset.status == "PENDING", 1))),
        func.count(case((Dataset.status.in_(["PROCESSING", "PROCESSING_PIPELINE"]), 1))),
        func.count(case((Dataset.status == "COMPLETED", 1))),
        func.count(case((Dataset.status == "FAILED", 1))),
        func.count(Dataset.id),
    ).first()

    datasets_pending = (ds_agg[0] or 0) if ds_agg else 0
    datasets_processing = (ds_agg[1] or 0) if ds_agg else 0
    datasets_completed = (ds_agg[2] or 0) if ds_agg else 0
    datasets_failed = (ds_agg[3] or 0) if ds_agg else 0
    total_datasets = (ds_agg[4] or 0) if ds_agg else 0

    # Model info via scalar count
    total_model_runs = db.query(func.count(ModelRun.id)).scalar() or 0
    latest_model = db.query(ModelRun).order_by(
        ModelRun.training_timestamp.desc()
    ).first()

    # Anomaly score distribution (SQL bucketed aggregation — zero ORM allocations)
    dist_row = db.query(
        func.count(case((AnomalyResult.anomaly_score <= 20, 1))),
        func.count(case(((AnomalyResult.anomaly_score > 20) & (AnomalyResult.anomaly_score <= 40), 1))),
        func.count(case(((AnomalyResult.anomaly_score > 40) & (AnomalyResult.anomaly_score <= 60), 1))),
        func.count(case(((AnomalyResult.anomaly_score > 60) & (AnomalyResult.anomaly_score <= 80), 1))),
        func.count(case((AnomalyResult.anomaly_score > 80, 1)))
    ).filter(AnomalyResult.anomaly_score.isnot(None)).first()

    if dist_row:
        anomaly_distribution = {
            "0-20": dist_row[0] or 0,
            "20-40": dist_row[1] or 0,
            "40-60": dist_row[2] or 0,
            "60-80": dist_row[3] or 0,
            "80-100": dist_row[4] or 0,
        }
    else:
        anomaly_distribution = {"0-20": 0, "20-40": 0, "40-60": 0, "60-80": 0, "80-100": 0}

    # Recent alerts: Prioritize highest anomaly score (critical leads) first
    recent_alerts = db.query(
        Alert.id,
        Alert.entity_type,
        Alert.entity_id,
        Alert.priority,
        Alert.anomaly_score,
        Alert.status,
        Alert.created_at
    ).order_by(
        Alert.anomaly_score.desc().nullslast(),
        Alert.created_at.desc()
    ).limit(10).all()

    recent_alerts_list = [
        {
            "id": r[0],
            "entity_type": r[1],
            "entity_id": r[2],
            "priority": r[3],
            "anomaly_score": round(r[4], 1) if r[4] else 0,
            "status": r[5],
            "created_at": r[6].isoformat() if r[6] else None,
        }
        for r in recent_alerts
    ]

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
