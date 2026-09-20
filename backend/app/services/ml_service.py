"""
BTC-SHIELD Machine Learning Service
Genuine ML: Isolation Forest for anomaly detection, DBSCAN for behavioral clustering.
Model versioning, artifact persistence, and evaluation metrics.
"""
from sqlalchemy.orm import Session
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import numpy as np
import joblib
import os
import uuid
from datetime import datetime
from app.models.models import BehavioralFeature, ModelRun, AnomalyResult
import logging

logger = logging.getLogger(__name__)

# Feature columns used for ML
FEATURE_COLUMNS = [
    "tx_count", "total_sent", "total_received", "net_flow",
    "amount_mean", "amount_std", "amount_variance",
    "fan_in", "fan_out", "fan_ratio",
    "fee_mean", "fee_to_value_ratio",
    "tx_velocity", "inter_arrival_mean", "burstiness",
    "active_duration_hours", "hour_entropy",
    "unique_counterparties", "counterparty_entropy",
    "unique_ip_count", "unique_asn_count", "unique_country_count",
    "asn_entropy",
]

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "ml_models")


def _extract_feature_matrix(features_records: list[BehavioralFeature]) -> tuple[np.ndarray, list]:
    """Extract feature matrix from behavioral feature records."""
    X = []
    valid_entities = []
    for f in features_records:
        if not f.features:
            continue
        row = []
        for col in FEATURE_COLUMNS:
            val = f.features.get(col, 0)
            try:
                row.append(float(val) if val is not None else 0.0)
            except (ValueError, TypeError):
                row.append(0.0)
        X.append(row)
        valid_entities.append(f)

    if not X:
        return np.array([]), []

    X = np.array(X, dtype=float)
    # Replace NaN/Inf with 0
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    return X, valid_entities


def train_isolation_forest(db: Session, dataset_id: int) -> int | None:
    """
    Train Isolation Forest on wallet behavioral features.
    Returns model_run_id or None if insufficient data.
    """
    features_records = db.query(BehavioralFeature).filter(
        BehavioralFeature.entity_type == "WALLET"
    ).all()

    if len(features_records) < 5:
        logger.warning("Insufficient data for Isolation Forest training (need >= 5 entities)")
        return None

    X, valid_entities = _extract_feature_matrix(features_records)
    if len(X) < 5:
        return None

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Determine contamination based on data size
    contamination = min(0.1, max(0.01, 5 / len(X)))

    # Train Isolation Forest
    model_version = f"IF-{uuid.uuid4().hex[:8]}"
    random_state = 42

    clf = IsolationForest(
        contamination=contamination,
        n_estimators=100,
        max_samples="auto",
        random_state=random_state,
        n_jobs=-1
    )
    clf.fit(X_scaled)

    # Get raw anomaly scores (decision_function: negative = more anomalous)
    raw_scores = clf.decision_function(X_scaled)
    predictions = clf.predict(X_scaled)

    # Scale to 0-100 (higher = more anomalous)
    inverted = -raw_scores  # invert so higher = more anomalous
    min_s, max_s = np.min(inverted), np.max(inverted)
    if max_s > min_s:
        scaled_scores = ((inverted - min_s) / (max_s - min_s)) * 100
    else:
        scaled_scores = np.full(len(inverted), 50.0)

    # Evaluation metrics
    n_anomalies = int(np.sum(predictions == -1))
    n_normal = int(np.sum(predictions == 1))

    eval_metrics = {
        "n_samples": len(X),
        "n_features": len(FEATURE_COLUMNS),
        "n_anomalies_detected": n_anomalies,
        "n_normal": n_normal,
        "anomaly_ratio": n_anomalies / len(X) if len(X) > 0 else 0,
        "contamination": contamination,
        "score_mean": float(np.mean(scaled_scores)),
        "score_std": float(np.std(scaled_scores)),
        "score_min": float(np.min(scaled_scores)),
        "score_max": float(np.max(scaled_scores)),
        "score_median": float(np.median(scaled_scores)),
    }

    # Save model artifact
    os.makedirs(MODEL_DIR, exist_ok=True)
    artifact_path = os.path.join(MODEL_DIR, f"{model_version}.joblib")
    joblib.dump({"model": clf, "scaler": scaler, "feature_columns": FEATURE_COLUMNS}, artifact_path)

    # Record model run
    run = ModelRun(
        model_type="IsolationForest",
        model_version=model_version,
        feature_schema_version="2.0",
        parameters={
            "contamination": contamination,
            "n_estimators": 100,
            "max_samples": "auto",
            "random_state": random_state,
            "n_features": len(FEATURE_COLUMNS),
            "feature_columns": FEATURE_COLUMNS,
        },
        dataset_id=dataset_id,
        training_timestamp=datetime.utcnow(),
        evaluation_metrics=eval_metrics,
        artifact_path=artifact_path,
        status="COMPLETED"
    )
    db.add(run)
    db.flush()

    # Store anomaly results
    for i, entity in enumerate(valid_entities):
        ar = AnomalyResult(
            model_run_id=run.id,
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            anomaly_score=float(scaled_scores[i]),
            cluster_id=None
        )
        db.add(ar)

    db.commit()
    logger.info(
        f"Isolation Forest trained: {n_anomalies} anomalies detected out of {len(X)} entities. "
        f"Model version: {model_version}"
    )
    return run.id


def train_dbscan(db: Session, dataset_id: int) -> int | None:
    """
    Train DBSCAN clustering on wallet behavioral features.
    Groups entities by behavioral similarity.
    """
    features_records = db.query(BehavioralFeature).filter(
        BehavioralFeature.entity_type == "WALLET"
    ).all()

    if len(features_records) < 5:
        logger.warning("Insufficient data for DBSCAN clustering")
        return None

    X, valid_entities = _extract_feature_matrix(features_records)
    if len(X) < 5:
        return None

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # DBSCAN clustering
    model_version = f"DBSCAN-{uuid.uuid4().hex[:8]}"

    # Adaptive eps based on data characteristics
    from sklearn.neighbors import NearestNeighbors
    nn = NearestNeighbors(n_neighbors=min(5, len(X)))
    nn.fit(X_scaled)
    distances, _ = nn.kneighbors(X_scaled)
    eps = float(np.percentile(distances[:, -1], 90))
    eps = max(eps, 0.5)  # minimum eps

    clusterer = DBSCAN(eps=eps, min_samples=max(2, len(X) // 20))
    labels = clusterer.fit_predict(X_scaled)

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int(np.sum(labels == -1))

    # Evaluation
    eval_metrics = {
        "n_samples": len(X),
        "n_clusters": n_clusters,
        "n_noise_points": n_noise,
        "noise_ratio": n_noise / len(X) if len(X) > 0 else 0,
        "eps": eps,
        "min_samples": max(2, len(X) // 20),
    }

    # Silhouette score (only if we have >= 2 clusters and not all noise)
    if n_clusters >= 2 and n_noise < len(X):
        non_noise_mask = labels != -1
        if np.sum(non_noise_mask) > 1:
            try:
                sil = silhouette_score(X_scaled[non_noise_mask], labels[non_noise_mask])
                eval_metrics["silhouette_score"] = float(sil)
            except Exception:
                eval_metrics["silhouette_score"] = None

    # Cluster size distribution
    cluster_sizes = {}
    for label in labels:
        key = int(label)
        cluster_sizes[key] = cluster_sizes.get(key, 0) + 1
    eval_metrics["cluster_sizes"] = cluster_sizes

    # Record model run
    run = ModelRun(
        model_type="DBSCAN",
        model_version=model_version,
        feature_schema_version="2.0",
        parameters={
            "eps": eps,
            "min_samples": max(2, len(X) // 20),
            "metric": "euclidean",
            "n_features": len(FEATURE_COLUMNS),
        },
        dataset_id=dataset_id,
        training_timestamp=datetime.utcnow(),
        evaluation_metrics=eval_metrics,
        status="COMPLETED"
    )
    db.add(run)
    db.flush()

    # Store cluster assignments as anomaly results
    for i, entity in enumerate(valid_entities):
        # Noise points in DBSCAN (label=-1) are potentially anomalous
        cluster_label = int(labels[i])
        ar = AnomalyResult(
            model_run_id=run.id,
            entity_type=entity.entity_type,
            entity_id=entity.entity_id,
            anomaly_score=100.0 if cluster_label == -1 else 0.0,
            cluster_id=cluster_label
        )
        db.add(ar)

    db.commit()
    logger.info(
        f"DBSCAN completed: {n_clusters} clusters, {n_noise} noise points. "
        f"Model version: {model_version}"
    )
    return run.id


def run_full_ml_pipeline(db: Session, dataset_id: int):
    """Run the complete ML pipeline: Isolation Forest + DBSCAN."""
    logger.info(f"Starting ML pipeline for dataset {dataset_id}")
    if_run = train_isolation_forest(db, dataset_id)
    dbscan_run = train_dbscan(db, dataset_id)
    logger.info(f"ML pipeline complete. IF run: {if_run}, DBSCAN run: {dbscan_run}")
    return {"isolation_forest_run": if_run, "dbscan_run": dbscan_run}
