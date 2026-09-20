import pytest
from app.services.ingestion_service import process_dataset
from app.services.feature_service import compute_all_features
from app.services.ml_service import run_full_ml_pipeline
from app.services.evidence_service import generate_evidence
from app.models.models import Dataset, Evidence

def test_evidence_generation(db_session):
    ds = Dataset(name="ev_test.csv", filename="ev_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    # Create bursty high fan-out transactions
    csv_rows = ["txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn"]
    for i in range(12):
        csv_rows.append(
            f"tx_ev_{i},2026-03-01T10:{i:02d}:00Z,500,p2pkh,wallet_target_alpha,out_addr_{i},50000,49500,10.0.0.{i+1},10.0.0.100,8333,8333,US,AS15169"
        )
    csv_data = "\n".join(csv_rows).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    compute_all_features(db_session)
    run_full_ml_pipeline(db_session, ds.id)
    ev_count = generate_evidence(db_session)

    assert ev_count > 0

    evidences = db_session.query(Evidence).all()
    assert len(evidences) > 0

    # Ensure each evidence has valid category, observation, strength
    for e in evidences:
        assert e.category in ["MODEL", "CLUSTER", "AMOUNT", "TRANSACTION", "TEMPORAL", "NETWORK", "GEOGRAPHIC", "GRAPH"]
        assert len(e.observation) > 10
        assert 0.0 <= e.strength <= 1.0
