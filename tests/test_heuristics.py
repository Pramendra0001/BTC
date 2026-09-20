import pytest
from app.services.ingestion_service import process_dataset
from app.services.heuristics_service import (
    compute_entropy, detect_peeling_chains, detect_mixing_patterns,
    analyze_transaction_heuristics, get_heuristics_summary
)
from app.models.models import Dataset

def test_entropy_computation():
    assert compute_entropy([]) == 0.0
    assert compute_entropy([0, 0]) == 0.0
    # Uniform distribution across 2 equal values has 1 bit of entropy
    assert abs(compute_entropy([10.0, 10.0]) - 1.0) < 0.001

def test_peeling_chain_detection(db_session):
    ds = Dataset(name="peeling_test.csv", filename="peeling_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    # Create 3 sequential peeling hops:
    # Hop 1: in=10 BTC -> peel 0.5 BTC to recipient1, change 9.5 BTC to change1
    # Hop 2: in=9.5 BTC from change1 -> peel 0.5 BTC to recipient2, change 9.0 BTC to change2
    # Hop 3: in=9.0 BTC from change2 -> peel 0.5 BTC to recipient3, change 8.5 BTC to change3
    csv_rows = [
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn",
        "tx_p1,2026-03-01T10:00:00Z,500,p2pkh,addr_root,addr_peel_1;addr_change_1,10.0,0.5;9.5,10.0.0.1,10.0.0.2,8333,8333,US,AS15169",
        "tx_p2,2026-03-01T10:05:00Z,500,p2pkh,addr_change_1,addr_peel_2;addr_change_2,9.5,0.5;9.0,10.0.0.1,10.0.0.2,8333,8333,US,AS15169",
        "tx_p3,2026-03-01T10:10:00Z,500,p2pkh,addr_change_2,addr_peel_3;addr_change_3,9.0,0.5;8.5,10.0.0.1,10.0.0.2,8333,8333,US,AS15169"
    ]
    csv_data = "\n".join(csv_rows).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)

    chains = detect_peeling_chains(db_session, min_hops=2)
    assert len(chains) > 0

    first_chain = chains[0]
    assert first_chain["hop_count"] >= 2
    assert first_chain["confidence_score"] > 50.0
    assert len(first_chain["hops"]) >= 2
    assert first_chain["hops"][0]["peeled_amount"] == 0.5

def test_mixing_coinjoin_detection(db_session):
    ds = Dataset(name="mix_test.csv", filename="mix_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    # Equal denomination CoinJoin with 4 equal outputs of 0.1 BTC
    csv_rows = [
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn",
        "tx_cj1,2026-03-01T11:00:00Z,1000,p2pkh,in1;in2;in3;in4,cj_out1;cj_out2;cj_out3;cj_out4,0.11;0.11;0.11;0.11,0.1;0.1;0.1;0.1,192.168.1.1,10.0.0.1,8333,8333,US,AS1234"
    ]
    csv_data = "\n".join(csv_rows).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)

    mixes = detect_mixing_patterns(db_session)
    assert len(mixes) > 0

    cj_tx = next((m for m in mixes if m["txid"] == "tx_cj1"), None)
    assert cj_tx is not None
    assert cj_tx["pattern_type"] == "EQUAL_DENOMINATION_COINJOIN"
    assert cj_tx["max_equal_outputs"] == 4
    assert cj_tx["confidence_score"] >= 80.0

def test_transaction_heuristics_and_summary(db_session):
    ds = Dataset(name="fan_test.csv", filename="fan_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    # 1 input to 6 outputs (fan-out dispersion)
    outs = ";".join([f"dest_{i}" for i in range(6)])
    amounts = ";".join(["1000" for _ in range(6)])
    csv_rows = [
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn",
        f"tx_fan_01,2026-03-01T12:00:00Z,500,p2pkh,single_source,{outs},8500,{amounts},10.0.0.1,10.0.0.2,8333,8333,US,AS15169"
    ]
    csv_data = "\n".join(csv_rows).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)

    analysis = analyze_transaction_heuristics(db_session, "tx_fan_01")
    assert analysis["found"] is True
    assert analysis["output_count"] == 6
    assert "FAN_OUT_DISPERSION" in analysis["detected_patterns"]

    summary = get_heuristics_summary(db_session)
    assert "peeling_chains_detected" in summary
    assert "mixing_transactions_detected" in summary
    assert "fan_out_dispersion_count" in summary
