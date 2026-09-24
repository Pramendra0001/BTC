"""
BTC-SHIELD — Air-Gapped Zero-Egress Comprehensive Verification Test
SIH Problem Statement 26146: "AI-Powered Monitoring & Analysis of Bitcoin Transaction Traffic"

This test proves programmatically that BTC-SHIELD can ingest, process, engineer features,
train unsupervised ML models, construct NetworkX multigraphs, generate evidence, prioritize alerts,
and export forensic case dossiers with ZERO external network egress.
"""

import os
import socket
import urllib.request
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import settings
from app.main import app
from app.models.models import Dataset, User
from app.services.ingestion_service import process_dataset
from app.services.feature_service import compute_all_features
from app.services.ml_service import train_isolation_forest, train_dbscan
from app.services.graph_service import build_graph, compute_centrality
from app.services.evidence_service import generate_evidence
from app.services.alert_service import generate_alerts
from app.services.case_service import create_case, generate_report

@pytest.fixture
def airgap_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed an admin user for RBAC & investigator tests
        admin = User(
            id=1,
            username="admin",
            email="admin@btcshield.gov",
            hashed_password="hash",
            role="ADMINISTRATOR",
            is_active=True
        )
        db.add(admin)
        db.commit()
        yield db
    finally:
        db.close()

def test_full_airgap_workflow_zero_egress(airgap_db, monkeypatch):
    """
    Guards all network sockets and urllib requests to enforce a strict air-gap boundary.
    Any attempt to connect to an external IP or domain immediately raises an exception.
    """
    external_calls = []

    real_connect = socket.socket.connect
    def airgap_guard_connect(self, address):
        host = address[0] if isinstance(address, tuple) and len(address) > 0 else str(address)
        # Allow only loopback/in-process connections
        if host not in ("127.0.0.1", "localhost", "::1", "0.0.0.0"):
            external_calls.append(f"socket:{address}")
            raise RuntimeError(f"AIR-GAP VIOLATION: Socket call attempted to {address}")
        return real_connect(self, address)

    def airgap_guard_urlopen(*args, **kwargs):
        external_calls.append(f"urlopen:{args}")
        raise RuntimeError(f"AIR-GAP VIOLATION: urllib.request attempted to {args}")

    monkeypatch.setattr(socket.socket, "connect", airgap_guard_connect)
    monkeypatch.setattr(urllib.request, "urlopen", airgap_guard_urlopen)

    # 1. Dataset & Ingestion: Read from offline/datasets/sample_transactions.csv
    csv_path = os.path.join(os.path.dirname(__file__), "..", "offline", "datasets", "sample_transactions.csv")
    assert os.path.exists(csv_path), f"Sample dataset missing at {csv_path}"
    with open(csv_path, "rb") as f:
        csv_bytes = f.read()
    assert len(csv_bytes) > 0

    ds = Dataset(name="offline_test.csv", filename="sample_transactions.csv", format="csv")
    airgap_db.add(ds)
    airgap_db.commit()

    process_dataset(airgap_db, ds.id, csv_bytes)
    airgap_db.refresh(ds)
    assert ds.valid_records > 0
    assert ds.total_records > 0
    assert ds.status == "COMPLETED"


    # 2. Feature Engineering: 23 continuous features
    compute_all_features(airgap_db)

    # 3. ML Pipeline: Isolation Forest & DBSCAN
    if_run = train_isolation_forest(airgap_db, ds.id)
    assert if_run is not None

    dbscan_run = train_dbscan(airgap_db, ds.id)
    assert dbscan_run is not None

    # 4. Graph Analytics: NetworkX multigraph & centrality
    G = build_graph(airgap_db)
    assert len(G.nodes) > 0
    centrality = compute_centrality(G)
    assert isinstance(centrality, dict)

    # 5. Evidence Engine: Deterministic rule-based observations
    evidence_count = generate_evidence(airgap_db)
    assert evidence_count > 0

    # 6. Alert Prioritizer: Compound risk scores
    alert_count = generate_alerts(airgap_db)
    assert alert_count > 0


    # 7. Case Management & Dossier Export
    case = create_case(
        db=airgap_db,
        title="Air-Gapped Forensic Verification Case",
        description="SIH 26146 offline test",
        priority="HIGH",
        investigator_id=1
    )
    assert case.id is not None

    dossier = generate_report(db=airgap_db, case_id=case.id)
    assert dossier is not None
    assert dossier.get("report_type") == "INVESTIGATION_REPORT"
    assert "summary" in dossier


    # 8. System Status Telemetry Check via TestClient
    def override_get_db():
        try:
            yield airgap_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json() == {"status": "ok"}

    status_resp = client.get("/api/system/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["database"] == "OPERATIONAL"
    assert status_data["ml_service"] == "ok"
    assert status_data["ai_provider"] == "mock"
    assert status_data["offline_telemetry"]["external_api_calls"] == "NONE"
    assert status_data["offline_telemetry"]["internet_required"] == "NO"

    app.dependency_overrides.clear()

    # 9. Strict Air-Gap Verification: Zero external network calls
    assert len(external_calls) == 0, f"External network calls detected during air-gap test: {external_calls}"
