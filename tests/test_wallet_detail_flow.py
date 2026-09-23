import pytest
from app.models.models import Wallet, GraphEdge, Transaction

def test_wallet_detail_graphedge_relational_resolution(client):
    # Test that wallet detail resolves transactions and counterparties from GraphEdge
    response = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Query first available wallet
    w_list = client.get("/api/wallets/?limit=1", headers=headers)
    assert w_list.status_code == 200
    wallets = w_list.json().get("wallets", [])
    if wallets:
        addr = wallets[0]["address"]
        w_res = client.get(f"/api/wallets/{addr}", headers=headers)
        assert w_res.status_code == 200
        w_data = w_res.json()
        assert "address" in w_data
        assert "transactions" in w_data
        assert "counterparties" in w_data
        assert "evidence" in w_data
        assert isinstance(w_data["transactions"], list)
        assert isinstance(w_data["counterparties"], list)

def test_wallet_detail_not_found_returns_404(client):
    response = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    res = client.get("/api/wallets/nonexistent_wallet_xyz", headers=headers)
    assert res.status_code == 404

def test_graph_ego_network_resolution(client):
    response = client.post("/api/auth/login", json={
        "username": "testadmin",
        "password": "testadmin123"
    })
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    w_list = client.get("/api/wallets/?limit=1", headers=headers)
    wallets = w_list.json().get("wallets", [])
    if wallets:
        addr = wallets[0]["address"]
        g_res = client.get(f"/api/graph/WALLET/{addr}?hops=1", headers=headers)
        assert g_res.status_code == 200
        g_data = g_res.json()
        assert "nodes" in g_data
        assert "edges" in g_data
        assert "stats" in g_data
        assert isinstance(g_data["nodes"], list)
        assert isinstance(g_data["edges"], list)
        node_ids = {n["data"]["id"] for n in g_data["nodes"]}
        # Every edge must reference valid node IDs
        for e in g_data["edges"]:
            assert e["data"]["source"] in node_ids
            assert e["data"]["target"] in node_ids
