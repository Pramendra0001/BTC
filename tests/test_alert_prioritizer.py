import pytest
from app.services.ingestion_service import process_dataset
from app.services.feature_service import compute_all_features
from app.services.ml_service import run_full_ml_pipeline
from app.services.evidence_service import generate_evidence
from app.services.alert_service import generate_alerts
from app.models.models import Dataset, Alert

def test_alert_prioritization(db_session):
    ds = Dataset(name="alert_test.csv", filename="alert_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    csv_rows = ["txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn"]
    for i in range(12):
        csv_rows.append(
            f"tx_al_{i},2026-03-01T10:{i:02d}:00Z,500,p2pkh,wallet_alert_focus,recipient_{i},100000,99500,10.0.0.{i+1},10.0.0.200,8333,8333,US,AS15169"
        )
    csv_data = "\n".join(csv_rows).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    compute_all_features(db_session)
    run_full_ml_pipeline(db_session, ds.id)
    generate_evidence(db_session)
    alert_count = generate_alerts(db_session)

    assert alert_count > 0

    alerts = db_session.query(Alert).all()
    assert len(alerts) > 0

    for a in alerts:
        assert a.priority in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert 0.0 <= a.anomaly_score <= 100.0
        assert 0.0 <= a.confidence <= 1.0
        assert a.status in ["NEW", "REVIEWING", "RESOLVED", "DISMISSED", "CASE_CREATED"]
        assert isinstance(a.contributing_signals, list)
