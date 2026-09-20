import pytest

def test_health_check(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_system_status(client):
    response = client.get("/api/system/status")
    assert response.status_code == 200
    data = response.json()
    assert data["database"] == "OPERATIONAL"
    assert data["ml_service"] == "ok"

def test_auth_login(client):
    # Test valid login
    response = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Test invalid credentials
    bad_res = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "wrongpassword"
    })
    assert bad_res.status_code == 401

def test_dashboard_endpoint(client):
    # Authenticate
    auth_res = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/dashboard/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "stats" in data
    assert "alerts" in data
    assert "anomalyDistribution" in data

def test_case_lifecycle(client):
    auth_res = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create Case
    create_res = client.post("/api/cases/", headers=headers, json={
        "title": "Operation Unit Test",
        "description": "Integration test for case management lifecycle",
        "priority": "HIGH"
    })
    assert create_res.status_code == 200
    case_id = create_res.json()["id"]

    # Get Case
    get_res = client.get(f"/api/cases/{case_id}", headers=headers)
    assert get_res.status_code == 200
    assert get_res.json()["title"] == "Operation Unit Test"

    # Update Case Status
    patch_res = client.patch(f"/api/cases/{case_id}", headers=headers, json={
        "status": "ACTIVE"
    })
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "ACTIVE"

    # Add Note
    note_res = client.post(f"/api/cases/{case_id}/notes", headers=headers, json={
        "content": "Initial target identified from ML cluster."
    })
    assert note_res.status_code == 200
    assert "content" in note_res.json()

    # Get Forensic Report
    report_res = client.get(f"/api/cases/{case_id}", headers=headers)
    assert report_res.status_code == 200

def test_heuristics_endpoints(client):
    res_summary = client.get("/api/heuristics/summary")
    assert res_summary.status_code == 200
    data = res_summary.json()
    assert "peeling_chains_detected" in data
    assert "mixing_transactions_detected" in data

    res_peel = client.get("/api/heuristics/peeling-chains")
    assert res_peel.status_code == 200
    assert isinstance(res_peel.json(), list)

    res_mixing = client.get("/api/heuristics/mixing-patterns")
    assert res_mixing.status_code == 200
    assert isinstance(res_mixing.json(), list)

def test_data_quality_endpoints(client):
    res = client.get("/api/data-quality/summary")
    assert res.status_code == 200
    data = res.json()
    assert "overall_health_score" in data
    assert "enrichment_coverage" in data

    res_rejected = client.get("/api/data-quality/rejected-records")
    assert res_rejected.status_code == 200
    assert "rejected_records" in res_rejected.json()

def test_audit_logs_and_users(client):
    # Authenticate to generate an audit log
    client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })

    # Query audit trail
    res_audit = client.get("/api/audit-logs")
    assert res_audit.status_code == 200
    assert "audit_logs" in res_audit.json()
    assert res_audit.json()["total"] >= 1

    # Query users
    res_users = client.get("/api/users")
    assert res_users.status_code == 200
    assert len(res_users.json()) >= 1

def test_jobs_endpoints(client):
    res_jobs = client.get("/api/jobs")
    assert res_jobs.status_code == 200
    jobs = res_jobs.json()
    assert isinstance(jobs, list)
    assert len(jobs) >= 1
