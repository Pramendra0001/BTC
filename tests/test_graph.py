import pytest
from app.services.ingestion_service import process_dataset
from app.services.graph_service import build_graph, compute_centrality, get_subgraph, persist_graph
from app.models.models import Dataset, GraphNode, GraphEdge

def test_graph_construction_and_centrality(db_session):
    ds = Dataset(name="graph_test.csv", filename="graph_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    csv_data = (
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn\n"
        "tx_g1,2026-03-01T10:00:00Z,500,p2pkh,node_wallet_1,node_wallet_2,50000,49500,10.0.0.1,10.0.0.2,8333,8333,US,AS15169\n"
        "tx_g2,2026-03-01T10:05:00Z,500,p2pkh,node_wallet_2,node_wallet_3,49500,49000,10.0.0.1,10.0.0.3,8333,8333,US,AS15169\n"
    ).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    G = build_graph(db_session)

    # Verify nodes
    assert G.has_node("WALLET:node_wallet_1")
    assert G.has_node("WALLET:node_wallet_2")
    assert G.has_node("TX:tx_g1")
    assert G.has_node("IP:10.0.0.1")

    # Verify edges
    assert G.has_edge("WALLET:node_wallet_1", "TX:tx_g1")
    assert G.has_edge("TX:tx_g1", "WALLET:node_wallet_2")

    # Centrality
    centrality = compute_centrality(G)
    assert "WALLET:node_wallet_2" in centrality
    assert centrality["WALLET:node_wallet_2"]["degree"] > 0

    # Subgraph extraction
    sub = get_subgraph(db_session, "WALLET", "node_wallet_1", hops=1)
    assert len(sub["nodes"]) > 0
    assert len(sub["edges"]) > 0
    assert sub["stats"]["center_node"] == "WALLET:node_wallet_1"

    # Persistence
    persist_graph(db_session)
    gn_count = db_session.query(GraphNode).count()
    ge_count = db_session.query(GraphEdge).count()
    assert gn_count > 0
    assert ge_count > 0
