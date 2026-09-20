"""
BTC-SHIELD Data Quality Subsystem Endpoints
Provides system-wide ingestion audit metrics, validation rates, enrichment coverage, and quarantined records.
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.database import get_db
from app.models.models import Dataset, RawRecord, Transaction, NetworkObservation

router = APIRouter()

@router.get("/summary")
def get_data_quality_summary(db: Session = Depends(get_db)):
    """Aggregated data quality and enrichment metrics across all ingested datasets."""
    datasets = db.query(Dataset).all()
    
    total_datasets = len(datasets)
    total_records = sum(d.total_records or 0 for d in datasets)
    valid_records = sum(d.valid_records or 0 for d in datasets)
    invalid_records = sum(d.invalid_records or 0 for d in datasets)
    duplicate_records = sum(d.duplicate_records or 0 for d in datasets)
    
    overall_health_score = round((valid_records / total_records * 100.0), 1) if total_records > 0 else 100.0

    # Format breakdown
    format_counts = {}
    for d in datasets:
        fmt = (d.format or "UNKNOWN").upper()
        format_counts[fmt] = format_counts.get(fmt, 0) + (d.total_records or 0)

    # Enrichment coverage
    total_net_obs = db.query(NetworkObservation).count()
    geoip_resolved = db.query(NetworkObservation).filter(
        NetworkObservation.geo_country.isnot(None),
        NetworkObservation.geo_country != "",
        NetworkObservation.geo_country != "UNKNOWN"
    ).count() if total_net_obs > 0 else 0

    asn_resolved = db.query(NetworkObservation).filter(
        NetworkObservation.asn.isnot(None),
        NetworkObservation.asn != "",
        NetworkObservation.asn != "UNKNOWN"
    ).count() if total_net_obs > 0 else 0

    total_txs = db.query(Transaction).count()
    txs_with_net = db.query(NetworkObservation.transaction_id).distinct().count() if total_net_obs > 0 else 0

    enrichment_coverage = {
        "network_observations_total": total_net_obs,
        "geoip_resolution_pct": round((geoip_resolved / total_net_obs * 100.0), 1) if total_net_obs > 0 else 0.0,
        "asn_resolution_pct": round((asn_resolved / total_net_obs * 100.0), 1) if total_net_obs > 0 else 0.0,
        "tx_network_correlation_pct": round((txs_with_net / total_txs * 100.0), 1) if total_txs > 0 else 0.0
    }

    return {
        "total_datasets": total_datasets,
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "duplicate_records": duplicate_records,
        "overall_health_score": overall_health_score,
        "format_breakdown": format_counts,
        "enrichment_coverage": enrichment_coverage,
        "datasets": [
            {
                "id": d.id,
                "name": d.name,
                "format": d.format,
                "status": d.status,
                "total_records": d.total_records,
                "valid_records": d.valid_records,
                "invalid_records": d.invalid_records,
                "duplicate_records": d.duplicate_records,
                "health_score": round((d.valid_records / d.total_records * 100.0), 1) if (d.total_records or 0) > 0 else 100.0,
                "created_at": d.created_at.isoformat() if d.created_at else None
            }
            for d in datasets
        ]
    }

@router.get("/rejected-records")
def get_rejected_records(
    dataset_id: int = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Retrieve isolated malformed/quarantined records with failure cause and line number."""
    query = db.query(RawRecord).filter(RawRecord.is_valid == False)
    if dataset_id:
        query = query.filter(RawRecord.dataset_id == dataset_id)

    total = query.count()
    records = query.order_by(RawRecord.id.desc()).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "rejected_records": [
            {
                "id": r.id,
                "dataset_id": r.dataset_id,
                "line_number": r.line_number,
                "error_message": r.error_message,
                "raw_data": r.raw_data,
                "created_at": r.created_at.isoformat() if r.created_at else None
            }
            for r in records
        ]
    }
