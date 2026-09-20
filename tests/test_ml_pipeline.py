import pytest
from app.services.ingestion_service import process_dataset
from app.services.feature_service import compute_all_features
from app.services.ml_service import run_full_ml_pipeline, train_isolation_forest, train_dbscan
from app.models.models import Dataset, ModelRun, AnomalyResult

def test_ml_pipeline_execution(db_session):
    ds = Dataset(name="ml_test.csv", filename="ml_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    # Generate 10 entities to allow IF & DBSCAN training
    csv_rows = ["txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn"]
    for i in range(12):
        csv_rows.append(
            f"tx_ml_{i},2026-03-01T10:{i:02d}:00Z,500,p2pkh,wallet_sender_{i},wallet_rec_{i},{10000 * (i+1)},{9500 * (i+1)},192.168.1.{i+10},10.0.0.1,8333,8333,US,AS15169"
        )
    csv_data = "\n".join(csv_rows).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    compute_all_features(db_session)

    res = run_full_ml_pipeline(db_session, ds.id)
    assert res["isolation_forest_run"] is not None
    assert res["dbscan_run"] is not None

    # Check ModelRun persistence
    model_runs = db_session.query(ModelRun).filter(ModelRun.dataset_id == ds.id).all()
    assert len(model_runs) >= 2

    # Check AnomalyResults
    anomalies = db_session.query(AnomalyResult).all()
    assert len(anomalies) > 0
    # Scores are scaled to 0-100
    for a in anomalies:
        if a.anomaly_score is not None:
            assert 0.0 <= a.anomaly_score <= 100.0
