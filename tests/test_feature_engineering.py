import pytest
from app.services.ingestion_service import process_dataset
from app.services.feature_service import compute_all_features, _shannon_entropy, _stats
from app.models.models import Dataset, BehavioralFeature, Wallet

def test_entropy_and_stats():
    # Uniform distribution entropy
    assert _shannon_entropy([10, 10]) == pytest.approx(1.0, 0.01)
    # Zero distribution
    assert _shannon_entropy([0, 0]) == 0.0

    stats = _stats([10, 20, 30])
    assert stats["count"] == 3
    assert stats["mean"] == 20.0
    assert stats["min"] == 10
    assert stats["max"] == 30

def test_feature_engineering_pipeline(db_session):
    ds = Dataset(name="feat_test.csv", filename="feat_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    csv_data = (
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn\n"
        "tx_f1,2026-03-01T10:00:00Z,1000,p2pkh,addr_alpha,addr_beta,100000,99000,10.0.0.1,10.0.0.2,8333,8333,US,AS15169\n"
        "tx_f2,2026-03-01T10:01:00Z,1200,p2pkh,addr_alpha,addr_gamma,99000,97800,10.0.0.2,10.0.0.3,8333,8333,DE,AS24940\n"
        "tx_f3,2026-03-01T10:01:10Z,1500,p2pkh,addr_alpha,addr_delta,97800,96300,10.0.0.3,10.0.0.4,8333,8333,NL,AS13335\n"
    ).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    compute_all_features(db_session)

    bf = db_session.query(BehavioralFeature).filter(
        BehavioralFeature.entity_type == "WALLET",
        BehavioralFeature.entity_id == "addr_alpha"
    ).first()

    assert bf is not None
    f = bf.features
    assert f["tx_count"] == 3
    assert f["fan_in"] == 3
    assert f["unique_country_count"] >= 3
    assert f["unique_asn_count"] >= 3
    assert f["burstiness"] is not None
