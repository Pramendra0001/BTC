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
    # Test valid JSON login -> 200 + access_token
    response = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Test invalid credentials -> 401
    bad_res = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "wrongpassword"
    })
    assert bad_res.status_code == 401
    assert bad_res.json()["detail"] == "Incorrect username or password"

def test_openapi_login_contract(client):
    # Verify OpenAPI documentation contains UserLogin requestBody
    res = client.get("/api/openapi.json")
    assert res.status_code == 200
    openapi = res.json()
    login_post = openapi["paths"]["/api/auth/login"]["post"]
    assert "requestBody" in login_post
    content = login_post["requestBody"]["content"]
    assert "application/json" in content
    schema_ref = content["application/json"]["schema"]["$ref"]
    schema_key = schema_ref.split("/")[-1]
    assert schema_key == "UserLogin"
    schema = openapi["components"]["schemas"]["UserLogin"]
    assert "properties" in schema
    assert "username" in schema["properties"]
    assert "password" in schema["properties"]

def test_protected_endpoints_unauthenticated(client):
    # Protected endpoint rejects unauthenticated request
    res_me = client.get("/api/auth/me")
    assert res_me.status_code == 401

    res_dash = client.get("/api/dashboard/")
    assert res_dash.status_code == 401

def test_admin_register_user(client):
    # Authenticate as administrator
    auth_res = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    token = auth_res.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {token}"}

    # 1. Administrator JWT permits /api/auth/register
    reg_res = client.post("/api/auth/register", json={
        "username": "newinvestigator",
        "email": "investigator@btcshield.gov",
        "password": "securepassword123",
        "role": "INVESTIGATOR"
    }, headers=admin_headers)
    assert reg_res.status_code == 200
    user_data = reg_res.json()
    assert user_data["username"] == "newinvestigator"
    assert user_data["role"] == "INVESTIGATOR"

    # 2. Login as newly registered user succeeds
    login_new = client.post("/api/auth/login", json={
        "username": "newinvestigator",
        "password": "securepassword123"
    })
    assert login_new.status_code == 200
    assert "access_token" in login_new.json()

    # 3. Non-administrator JWT cannot register users (403 Forbidden)
    new_token = login_new.json()["access_token"]
    non_admin_headers = {"Authorization": f"Bearer {new_token}"}
    unauth_reg = client.post("/api/auth/register", json={
        "username": "anotheruser",
        "email": "another@btcshield.gov",
        "password": "anotherpassword123",
        "role": "ANALYST"
    }, headers=non_admin_headers)
    assert unauth_reg.status_code == 403

    # 4. Unauthenticated request rejected (401 Unauthorized)
    no_auth_reg = client.post("/api/auth/register", json={
        "username": "noauthuser",
        "email": "noauth@btcshield.gov",
        "password": "password123",
        "role": "ANALYST"
    })
    assert no_auth_reg.status_code == 401

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
