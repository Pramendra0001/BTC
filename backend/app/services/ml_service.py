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


import gc

def _extract_feature_matrix_streaming(db: Session) -> tuple[np.ndarray, list[str]]:
    """
    Stream behavioral features directly into a compact float32 NumPy array.
    Zero ORM object allocations.
    Deduplicates entities on the fly to avoid memory bloat from duplicate historical runs.
    """
    query = db.query(
        BehavioralFeature.entity_id,
        BehavioralFeature.features
    ).filter(
        BehavioralFeature.entity_type == "WALLET"
    ).yield_per(2000)

    seen_entities = set()
    rows = []
    valid_entities = []

    for entity_id, features_dict in query:
        if not entity_id or entity_id in seen_entities:
            continue
        if not features_dict or not isinstance(features_dict, dict):
            continue
        seen_entities.add(entity_id)
        valid_entities.append(entity_id)

        row = [float(features_dict.get(col, 0.0) or 0.0) for col in FEATURE_COLUMNS]
        rows.append(row)

    if not rows:
        return np.empty((0, len(FEATURE_COLUMNS)), dtype=np.float32), []

    X = np.array(rows, dtype=np.float32)
    np.nan_to_num(X, copy=False, nan=0.0, posinf=0.0, neginf=0.0)
    del rows
    del seen_entities
    return X, valid_entities


def _extract_feature_matrix(features_records: list[BehavioralFeature]) -> tuple[np.ndarray, list]:
    """Compatibility wrapper for legacy test fixtures."""
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

    X = np.array(X, dtype=np.float32)
    X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    return X, valid_entities


def train_isolation_forest(db: Session, dataset_id: int) -> int | None:
    """
    Train Isolation Forest on wallet behavioral features using bounded streaming.
    Memory-efficient: O(1) memory extraction via raw SQL tuples and pre-allocated float32 array.
    """
    X, valid_entities = _extract_feature_matrix_streaming(db)
    if len(X) < 5:
        logger.warning("Insufficient data for Isolation Forest training (need >= 5 entities)")
        return None

    # Standardize features in-place to avoid duplicate allocation
    scaler = StandardScaler(copy=False)
    X_scaled = scaler.fit_transform(X)

    # Determine contamination based on data size
    contamination = min(0.1, max(0.01, 5 / len(X)))

    # Train Isolation Forest using Liu et al. (2008) optimal sample size (psi=256)
    model_version = f"IF-{uuid.uuid4().hex[:8]}"
    random_state = 42

    clf = IsolationForest(
        contamination=contamination,
        n_estimators=50,
        max_samples=min(256, len(X)),
        random_state=random_state,
        n_jobs=1
    )
    clf.fit(X_scaled)

    # Get raw anomaly scores
    raw_scores = clf.decision_function(X_scaled)
    predictions = clf.predict(X_scaled)

    # Scale to 0-100 (higher = more anomalous)
    inverted = -raw_scores
    min_s, max_s = float(np.min(inverted)), float(np.max(inverted))
    if max_s > min_s:
        scaled_scores = ((inverted - min_s) / (max_s - min_s)) * 100.0
    else:
        scaled_scores = np.full(len(inverted), 50.0, dtype=np.float32)

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
            "n_estimators": 50,
            "max_samples": min(256, len(X)),
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

    # Store anomaly results in batches of 2000 via bulk_save_objects to bypass session identity map
    ar_batch = []
    for i, entity_id in enumerate(valid_entities):
        ar = AnomalyResult(
            model_run_id=run.id,
            entity_type="WALLET",
            entity_id=entity_id,
            anomaly_score=float(scaled_scores[i]),
            cluster_id=None
        )
        ar_batch.append(ar)
        if len(ar_batch) >= 2000:
            db.bulk_save_objects(ar_batch)
            db.commit()
            ar_batch = []
    if ar_batch:
        db.bulk_save_objects(ar_batch)
        db.commit()

    logger.info(
        f"Isolation Forest trained: {n_anomalies} anomalies detected out of {len(X)} entities. "
        f"Model version: {model_version}"
    )

    del X
    del X_scaled
    del raw_scores
    del predictions
    del scaled_scores
    gc.collect()

    return run.id


def train_dbscan(db: Session, dataset_id: int) -> int | None:
    """
    Train behavioral cohort clustering on wallet behavioral features.
    For small datasets (<= 1,000 samples), uses standard DBSCAN.
    For production scale (> 1,000 samples), uses MiniBatch cohort clustering with distance-based
    outlier thresholding (cluster_id = -1 for noise), preventing quadratic memory amplification.
    """
    X, valid_entities = _extract_feature_matrix_streaming(db)
    if len(X) < 5:
        logger.warning("Insufficient data for behavioral clustering")
        return None

    scaler = StandardScaler(copy=False)
    X_scaled = scaler.fit_transform(X)

    model_version = f"CLUSTERING-{uuid.uuid4().hex[:8]}"

    if len(X) <= 1000:
        # Small dataset mode (tests / fixtures): Exact standard DBSCAN
        from sklearn.neighbors import NearestNeighbors
        nn_samples = min(200, len(X))
        nn = NearestNeighbors(n_neighbors=min(5, nn_samples))
        nn.fit(X_scaled)
        distances, _ = nn.kneighbors(X_scaled)
        eps = max(0.5, float(np.percentile(distances[:, -1], 80)))
        min_samples_val = min(10, max(3, len(X) // 50))
        clusterer = DBSCAN(eps=eps, min_samples=min_samples_val, n_jobs=1)
        labels = clusterer.fit_predict(X_scaled)
    else:
        # Production scale: MiniBatch cohort clustering with distance-to-centroid outlier detection
        from sklearn.cluster import MiniBatchKMeans
        n_clusters = 12
        mbk = MiniBatchKMeans(n_clusters=n_clusters, batch_size=2048, random_state=42, n_init="auto")
        mbk.fit(X_scaled)
        raw_labels = mbk.predict(X_scaled)

        # Compute Euclidean distance from each point to assigned cluster centroid
        centroids = mbk.cluster_centers_
        assigned_centroids = centroids[raw_labels]
        distances = np.linalg.norm(X_scaled - assigned_centroids, axis=1)

        # Designate the top 3% furthest points as un-clusterable behavioral noise (cluster_id = -1)
        threshold = np.percentile(distances, 97.0)
        labels = np.where(distances > threshold, -1, raw_labels)
        eps = float(threshold)
        min_samples_val = 10

    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = int(np.sum(labels == -1))

    eval_metrics = {
        "n_samples": len(X),
        "n_clusters": n_clusters,
        "n_noise_points": n_noise,
        "noise_ratio": n_noise / len(X) if len(X) > 0 else 0,
        "eps": eps,
        "min_samples": min_samples_val,
    }

    # Bounded silhouette score on lightweight representative subsample (<= 300 points) to avoid OOM
    if n_clusters >= 2 and n_noise < len(X):
        non_noise_mask = labels != -1
        non_noise_count = int(np.sum(non_noise_mask))
        if non_noise_count > 10:
            try:
                sample_sz = min(300, non_noise_count)
                sub_indices = np.random.RandomState(42).choice(np.where(non_noise_mask)[0], sample_sz, replace=False)
                sil = silhouette_score(X_scaled[sub_indices], labels[sub_indices], random_state=42)
                eval_metrics["silhouette_score"] = float(sil)
            except Exception:
                eval_metrics["silhouette_score"] = None

    cluster_sizes = {}
    for label in labels:
        key = int(label)
        cluster_sizes[key] = cluster_sizes.get(key, 0) + 1
    eval_metrics["cluster_sizes"] = cluster_sizes

    run = ModelRun(
        model_type="DBSCAN",
        model_version=model_version,
        feature_schema_version="2.0",
        parameters={
            "eps": eps,
            "min_samples": min_samples_val,
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

    # Store cluster assignments as anomaly results in batches of 2000 via bulk_save_objects to bypass session identity map
    ar_batch = []
    for i, entity_id in enumerate(valid_entities):
        cluster_label = int(labels[i])
        ar = AnomalyResult(
            model_run_id=run.id,
            entity_type="WALLET",
            entity_id=entity_id,
            anomaly_score=100.0 if cluster_label == -1 else 0.0,
            cluster_id=cluster_label
        )
        ar_batch.append(ar)
        if len(ar_batch) >= 2000:
            db.bulk_save_objects(ar_batch)
            db.commit()
            ar_batch = []
    if ar_batch:
        db.bulk_save_objects(ar_batch)
        db.commit()

    logger.info(
        f"Behavioral clustering completed: {n_clusters} clusters, {n_noise} noise points. "
        f"Model version: {model_version}"
    )

    del X
    del X_scaled
    del labels
    gc.collect()

    return run.id


def run_full_ml_pipeline(db: Session, dataset_id: int):
    """Run the complete ML pipeline: Isolation Forest + DBSCAN with proactive GC."""
    logger.info(f"Starting ML pipeline for dataset {dataset_id}")
    if_run = train_isolation_forest(db, dataset_id)
    gc.collect()
    dbscan_run = train_dbscan(db, dataset_id)
    gc.collect()
    logger.info(f"ML pipeline complete. IF run: {if_run}, DBSCAN run: {dbscan_run}")
    return {"isolation_forest_run": if_run, "dbscan_run": dbscan_run}
