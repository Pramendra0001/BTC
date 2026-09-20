"""
BTC-SHIELD Job / Task Status Service
Tracks pipeline asynchronous jobs (ingestion, feature extraction, ML training, graph indexing).
"""
from datetime import datetime
import uuid
import threading
from typing import Optional, Any

_lock = threading.Lock()

_JOBS: dict[str, dict[str, Any]] = {
    "job_init_ingest": {
        "job_id": "job_init_ingest",
        "job_type": "DATASET_INGESTION",
        "description": "Initial Synthetic Bitcoin & Network Ingestion (1,000 records)",
        "status": "COMPLETED",
        "progress_pct": 100,
        "message": "Processed 1,000 records: 1,000 valid, 0 invalid",
        "started_at": "2026-09-20T08:00:00Z",
        "completed_at": "2026-09-20T08:00:03Z",
        "duration_seconds": 3.12,
        "result": {"records_processed": 1000, "wallets_created": 6275, "ips_resolved": 1000}
    },
    "job_init_features": {
        "job_id": "job_init_features",
        "job_type": "FEATURE_ENGINEERING",
        "description": "Bulk 23-Dimensional Behavioral Feature Extraction",
        "status": "COMPLETED",
        "progress_pct": 100,
        "message": "Computed 23 behavioral features for 6,275 entities",
        "started_at": "2026-09-20T08:01:00Z",
        "completed_at": "2026-09-20T08:01:01Z",
        "duration_seconds": 0.85,
        "result": {"schema_version": "v2.0_bulk", "entities_profiled": 6275}
    },
    "job_init_ml": {
        "job_id": "job_init_ml",
        "job_type": "ML_TRAINING",
        "description": "Isolation Forest Anomaly Detection & DBSCAN Clustering",
        "status": "COMPLETED",
        "progress_pct": 100,
        "message": "Trained Isolation Forest (n=100) and DBSCAN (adaptive eps=1.24)",
        "started_at": "2026-09-20T08:02:00Z",
        "completed_at": "2026-09-20T08:02:02Z",
        "duration_seconds": 1.48,
        "result": {"alerts_generated": 775, "model_version": "v1.0"}
    }
}

def create_job(job_type: str, description: str) -> str:
    """Register a new job."""
    job_id = f"job_{uuid.uuid4().hex[:10]}"
    with _lock:
        _JOBS[job_id] = {
            "job_id": job_id,
            "job_type": job_type,
            "description": description,
            "status": "PENDING",
            "progress_pct": 0,
            "message": "Queued for processing",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "duration_seconds": None,
            "result": None
        }
    return job_id

def update_job(
    job_id: str,
    status: str,
    progress_pct: int,
    message: str,
    result: Optional[dict[str, Any]] = None
) -> None:
    """Update progress and status of a running job."""
    with _lock:
        if job_id in _JOBS:
            _JOBS[job_id]["status"] = status
            _JOBS[job_id]["progress_pct"] = progress_pct
            _JOBS[job_id]["message"] = message
            if result:
                _JOBS[job_id]["result"] = result
            if status in ("COMPLETED", "FAILED"):
                _JOBS[job_id]["completed_at"] = datetime.utcnow().isoformat()

def get_job(job_id: str) -> Optional[dict[str, Any]]:
    """Get status of a specific job."""
    with _lock:
        return _JOBS.get(job_id)

def list_jobs(limit: int = 50) -> list[dict[str, Any]]:
    """List recent jobs in descending order."""
    with _lock:
        jobs = list(_JOBS.values())
    jobs.sort(key=lambda j: j.get("started_at") or "", reverse=True)
    return jobs[:limit]
