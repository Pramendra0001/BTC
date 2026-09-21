import pytest
import os
import json
import io
import zipfile
from app.models.models import User, RoleEnum, Dataset, Transaction, Wallet, GraphEdge, Alert, Evidence
from app.services.ml_service import FEATURE_COLUMNS
from fastapi.testclient import TestClient
from app.main import app

def test_100k_manifest_and_readme_valid():
    """Verify 100k manifest.json and README.md exist and conform to schema."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    manifest_path = os.path.join(base_dir, "data", "samples", "btc_shield_100000_manifest.json")
    readme_path = os.path.join(base_dir, "data", "samples", "btc_shield_100000_README.md")

    assert os.path.exists(manifest_path), "100k manifest must exist"
    assert os.path.exists(readme_path), "100k README must exist"

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest.get("transaction_records") == 100000
    assert manifest.get("edge_records") == 350131
    assert manifest.get("wallet_records") == 45000
    assert "core_schema_columns" in manifest

def test_no_ml_ground_truth_leakage():
    """Verify that no evaluation or ground-truth columns leaked into ML feature set."""
    prohibited = {
        "scenario_label", "risk_score", "risk_level", "ground_truth",
        "cluster_id", "wallet_reuse_signal", "fan_out_signal", "fan_in_signal",
        "burst_signal", "geo_hopping_signal", "high_value_signal", "mixing_signal",
        "risk_profile", "scenario"
    }
    feature_set = set(FEATURE_COLUMNS)
    leakage = feature_set.intersection(prohibited)
    assert len(leakage) == 0, f"Detected ground-truth ML leakage in FEATURE_COLUMNS: {leakage}"

def test_safe_application_reset_permissions(client, db_session):
    """Ensure non-admin users cannot call reset-application-data."""
    # Register a normal viewer
    reg_resp = client.post("/api/auth/register", json={
        "username": "viewer_user",
        "email": "viewer@example.com",
        "password": "ViewerPassword123!"
    })
    assert reg_resp.status_code == 201

    login_resp = client.post("/api/auth/login", json={
        "username": "viewer_user",
        "password": "ViewerPassword123!"
    })
    token = login_resp.json()["access_token"]

    resp = client.post(
        "/api/datasets/admin/reset-application-data",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert resp.status_code == 403

def test_safe_application_reset_admin_execution(client, db_session):
    """Ensure admin can safely reset application intelligence data to baseline zeros."""
    login_resp = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    admin_token = login_resp.json()["access_token"]

    # Seed sample dataset and transaction
    ds = Dataset(name="test_reset.csv", filename="test_reset.csv", status="COMPLETED")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    tx = Transaction(dataset_id=ds.id, txid="tx_dummy_reset_01", fee=100.0, total_input=1000.0, total_output=900.0)
    db_session.add(tx)
    w = Wallet(address="1DummyWalletResetAddress999")
    db_session.add(w)
    db_session.commit()

    resp = client.post(
        "/api/datasets/admin/reset-application-data",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "EMPTY_BASELINE_VERIFIED"
    assert data["after_counts"]["transactions"] == 0
    assert data["after_counts"]["wallets"] == 0
    assert data["after_counts"]["datasets"] == 0

    # Ensure users and admin accounts are strictly preserved
    users_count = db_session.query(User).count()
    assert users_count > 0, "Users table must never be deleted"
