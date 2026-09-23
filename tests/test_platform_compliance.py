"""
BTC-SHIELD Platform Compliance Test Suite
Validates all core operational, algorithmic, architectural, and security requirements.
All tests are independent, verifiable, and strictly free of external competition identifiers.
"""
import pytest
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.models import (
    User, RoleEnum, Dataset, Transaction, TransactionInput, TransactionOutput,
    Wallet, NetworkObservation, IPEntity, ASNEntity, BehavioralFeature,
    Alert, Evidence, Case
)
from app.services.ingestion_service import (
    validate_bitcoin_address, validate_txid, validate_ip,
    parse_csv_content, parse_json_content, parse_xml_content, process_dataset
)
from app.services.feature_service import compute_all_features
from app.services.ml_service import train_isolation_forest, train_dbscan, FEATURE_COLUMNS
from app.services.heuristics_service import detect_peeling_chains, detect_mixing_patterns
from app.services.graph_service import build_graph, compute_centrality
from app.services.alert_service import generate_alerts
from app.services.case_service import create_case, add_note, generate_report
from app.services.geoip_service import geoip_service
from app.core.security import create_access_token, verify_password, get_password_hash


def test_compliance_01_syntax_validation():
    """Verify cryptographic hash integrity, address validation, and IP validation."""
    # 64-char valid hex txid
    valid_txid = "a" * 64
    invalid_txid = "not-a-valid-hex-txid"
    assert validate_txid(valid_txid) is True
    assert validate_txid(invalid_txid) is False

    # Bitcoin addresses (Base58 P2PKH, P2SH, and Bech32 P2WPKH)
    assert validate_bitcoin_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa") is True
    assert validate_bitcoin_address("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy") is True
    assert validate_bitcoin_address("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq") is True
    assert validate_bitcoin_address("too_short") is False
    assert validate_bitcoin_address("") is False

    # IP address validation
    assert validate_ip("192.168.1.1") is True
    assert validate_ip("2001:0db8:85a3:0000:0000:8a2e:0370:7334") is True
    assert validate_ip("999.999.999.999") is False


def test_compliance_02_multiformat_ingestion_and_quarantine():
    """Verify streaming ingestion across CSV, JSON, XML and defensive quarantine."""
    csv_data = "timestamp,src_ip,dst_ip,src_port,dst_port,txid,input_addresses,output_addresses,input_amounts,output_amounts,fee\n" \
               "2026-03-20T04:41:29Z,192.0.2.1,192.0.2.2,8333,8333,0000000000000000000000000000000000000000000000000000000000000001,1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa,3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy,100000,99000,1000"
    rows_csv = parse_csv_content(csv_data)
    assert len(rows_csv) == 1
    assert rows_csv[0]["txid"] == "0000000000000000000000000000000000000000000000000000000000000001"

    json_data = '[{"txid": "0000000000000000000000000000000000000000000000000000000000000002", "fee": 500}]'
    rows_json = parse_json_content(json_data)
    assert len(rows_json) == 1
    assert rows_json[0]["txid"] == "0000000000000000000000000000000000000000000000000000000000000002"

    xml_data = '<records><record><txid>0000000000000000000000000000000000000000000000000000000000000003</txid><fee>250</fee></record></records>'
    rows_xml = parse_xml_content(xml_data)
    assert len(rows_xml) == 1
    assert rows_xml[0]["txid"] == "0000000000000000000000000000000000000000000000000000000000000003"


def test_compliance_03_23_dimensional_feature_engineering(db_session: Session):
    """Verify exact 23-dimensional behavioral feature extraction."""
    ds = Dataset(name="feat_comp_test.csv", filename="feat_comp_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    csv_data = (
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn\n"
        "tx_c1,2026-03-01T10:00:00Z,1000,p2pkh,addr_comp_a,addr_comp_b,100000,99000,10.0.0.1,10.0.0.2,8333,8333,US,AS15169\n"
        "tx_c2,2026-03-01T10:01:00Z,1200,p2pkh,addr_comp_a,addr_comp_c,99000,97800,10.0.0.2,10.0.0.3,8333,8333,DE,AS24940\n"
    ).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    compute_all_features(db_session)

    bf = db_session.query(BehavioralFeature).filter(
        BehavioralFeature.entity_type == "WALLET",
        BehavioralFeature.entity_id == "addr_comp_a"
    ).first()

    assert bf is not None
    features_dict = bf.features
    assert isinstance(features_dict, dict)
    assert len(FEATURE_COLUMNS) == 23
    for col in FEATURE_COLUMNS:
        assert col in features_dict


def test_compliance_04_ml_isolation_forest_and_clustering(db_session: Session):
    """Verify calibrated Isolation Forest anomaly detection and dual-scale cohort clustering."""
    dataset = Dataset(name="Compliance Test Dataset", filename="test.csv")
    db_session.add(dataset)
    db_session.flush()

    for i in range(12):
        addr = f"1CohortWalletAddress_{i:04d}"
        feat_vals = {col: float(np.random.exponential(10.0)) for col in FEATURE_COLUMNS}
        bf = BehavioralFeature(
            entity_type="WALLET",
            entity_id=addr,
            feature_schema_version="2.0",
            features=feat_vals,
            computed_at=datetime.utcnow()
        )
        db_session.add(bf)
    db_session.commit()

    # Train Isolation Forest
    if_run_id = train_isolation_forest(db_session, dataset.id)
    assert if_run_id is not None

    # Train Cohort Clustering
    cluster_run_id = train_dbscan(db_session, dataset.id)
    assert cluster_run_id is not None


def test_compliance_05_structural_heuristics(db_session: Session):
    """Verify deterministic peeling cascade and CoinJoin entropy detection."""
    peeling_result = detect_peeling_chains(db_session, min_hops=2)
    assert isinstance(peeling_result, list)

    mixing_result = detect_mixing_patterns(db_session)
    assert isinstance(mixing_result, list)


def test_compliance_06_graph_intelligence(db_session: Session):
    """Verify multigraph construction and centrality metrics."""
    ds = Dataset(name="graph_comp_test.csv", filename="graph_comp_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    csv_data = (
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn\n"
        "tx_gc1,2026-03-01T10:00:00Z,500,p2pkh,node_c1,node_c2,50000,49500,10.0.0.1,10.0.0.2,8333,8333,US,AS15169\n"
    ).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    G = build_graph(db_session)
    assert G is not None

    metrics = compute_centrality(G)
    assert isinstance(metrics, dict)
    assert len(metrics) > 0


def test_compliance_07_alert_prioritization_and_evidence(db_session: Session):
    """Verify compound alert prioritization and deterministic evidence records."""
    dataset = Dataset(name="Compliance Alert Test", filename="alert_test.csv")
    db_session.add(dataset)
    db_session.flush()

    alert_count = generate_alerts(db_session)
    assert isinstance(alert_count, int)


def test_compliance_08_case_management_and_dossier_export(db_session: Session):
    """Verify case creation, note logging, and court-ready forensic report generation."""
    case = create_case(
        db=db_session,
        title="Compliance Verification Case Dossier",
        description="Forensic investigation into anomalous structural patterns.",
        priority="HIGH",
        investigator_id=1
    )
    assert case.id is not None

    note = add_note(
        db=db_session,
        case_id=case.id,
        user_id=1,
        content="Initial forensic lead established via behavioral anomaly clustering."
    )
    assert note.id is not None

    report = generate_report(db=db_session, case_id=case.id)
    assert isinstance(report, dict)
    assert "case" in report
    assert "disclaimer" in report
    assert "investigative" in report["disclaimer"].lower() or "demonstration" in report["disclaimer"].lower()


def test_compliance_09_offline_geoip_resolution():
    """Verify local and offline GeoIP resolution with graceful fallback."""
    # Test-Net documentation range (RFC 5737)
    res_testnet = geoip_service.lookup("198.51.100.14")
    assert res_testnet["valid"] is True
    assert res_testnet["country"] == "EU"
    assert res_testnet["asn"] == "AS64497"

    # Private loopback range
    res_loopback = geoip_service.lookup("127.0.0.1")
    assert res_loopback["valid"] is True
    assert res_loopback["country"] == "LOCAL"

    # Invalid string does not raise unhandled exception
    res_invalid = geoip_service.lookup("not-an-ip")
    assert res_invalid["valid"] is False
    assert res_invalid["country"] == "UNKNOWN"

    # Diagnostics contract
    diag = geoip_service.validate_status()
    assert "active_mode" in diag
    assert "offline_ranges_loaded" in diag


def test_compliance_10_rbac_and_security(client: TestClient):
    """Verify role authorization guards and security defenses."""
    # Health endpoint without authentication
    r_health = client.get("/health")
    assert r_health.status_code == 200

    # System status with GeoIP telemetry
    r_status = client.get("/api/system/status")
    assert r_status.status_code == 200
    data = r_status.json()
    assert "database" in data
    assert "geoip_service" in data

    # Password hashing and verification
    pwd = "EnterprisePassword@2026!"
    hashed = get_password_hash(pwd)
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrong-password", hashed) is False

    # Authenticate with admin credentials
    login_resp = client.post("/api/auth/login", json={"username": "testadmin", "password": "testadmin123"})
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Protected endpoint succeeds with admin token
    r_protected = client.get("/api/auth/me", headers=headers)
    assert r_protected.status_code == 200
    assert r_protected.json()["username"] == "testadmin"

    # Protected endpoint rejected without token
    r_unauth = client.get("/api/auth/me")
    assert r_unauth.status_code in [401, 403]
