"""
BTC-SHIELD Graph Intelligence Service
Bounded NetworkX graph extraction, local centrality computation, on-demand ego subgraphs,
and Cytoscape.js-compatible JSON export.
Memory-Optimized: Zero full-graph in-memory instantiations for request-time queries.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_
import networkx as nx
from app.models.models import (
    Wallet, Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, IPEntity, ASNEntity, GraphNode, GraphEdge,
    AnomalyResult
)
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def build_graph(db: Session, max_transactions: int = 500) -> nx.DiGraph:
    """
    Construct a bounded directed multigraph from entities and their relationships.
    Default max_transactions prevents out-of-memory crashes on large 100k datasets.
    """
    G = nx.DiGraph()

    # Pre-fetch anomalies for wallets
    anomaly_records = db.query(AnomalyResult).filter(AnomalyResult.entity_type == "WALLET").limit(1000).all()
    anomalies_map = {ar.entity_id: ar.anomaly_score for ar in anomaly_records}

    # Bounded transactions query
    transactions = db.query(Transaction).limit(max_transactions).all()
    tx_ids = [t.id for t in transactions]
    tx_map = {t.id: t for t in transactions}

    for tx in transactions:
        tx_node = f"TX:{tx.txid}"
        G.add_node(tx_node, **{
            "type": "TRANSACTION",
            "label": tx.txid[:12] + "...",
            "full_id": tx.txid,
            "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
            "fee": tx.fee,
            "total_input": tx.total_input,
            "total_output": tx.total_output,
        })

    # Bounded inputs and outputs for these transactions
    if tx_ids:
        inputs = db.query(TransactionInput).filter(TransactionInput.transaction_id.in_(tx_ids)).all()
        outputs = db.query(TransactionOutput).filter(TransactionOutput.transaction_id.in_(tx_ids)).all()

        for inp in inputs:
            w_addr = inp.wallet_address
            if w_addr:
                w_node = f"WALLET:{w_addr}"
                if w_node not in G:
                    G.add_node(w_node, type="WALLET", label=w_addr[:12] + "...", full_id=w_addr, anomaly_score=anomalies_map.get(w_addr))
                tx = tx_map.get(inp.transaction_id)
                if tx:
                    G.add_edge(w_node, f"TX:{tx.txid}", type="INPUT_OF", amount=inp.amount or 0)

        for out in outputs:
            w_addr = out.wallet_address
            if w_addr:
                w_node = f"WALLET:{w_addr}"
                if w_node not in G:
                    G.add_node(w_node, type="WALLET", label=w_addr[:12] + "...", full_id=w_addr, anomaly_score=anomalies_map.get(w_addr))
                tx = tx_map.get(out.transaction_id)
                if tx:
                    G.add_edge(f"TX:{tx.txid}", w_node, type="OUTPUT_OF", amount=out.amount or 0)

        # Network observations
        obs_records = db.query(NetworkObservation).filter(NetworkObservation.transaction_id.in_([t.txid for t in transactions])).all()
        for o in obs_records:
            if o.src_ip:
                ip_node = f"IP:{o.src_ip}"
                if ip_node not in G:
                    G.add_node(ip_node, type="IP", label=o.src_ip, full_id=o.src_ip)
                G.add_edge(ip_node, f"TX:{o.transaction_id}", type="OBSERVED_FROM", provenance="NetworkObservation")
                if o.asn:
                    asn_node = f"ASN:{o.asn}"
                    if asn_node not in G:
                        G.add_node(asn_node, type="ASN", label=o.asn, full_id=o.asn)
                    G.add_edge(ip_node, asn_node, type="BELONGS_TO_ASN", provenance="NetworkObservation")

    return G


def compute_centrality(G: nx.DiGraph) -> dict:
    """Compute graph centrality metrics for a bounded graph."""
    metrics = {}
    if G.number_of_nodes() == 0:
        return metrics

    try:
        degree = dict(G.degree())
        in_degree = dict(G.in_degree())
        out_degree = dict(G.out_degree())

        # PageRank (fast on bounded subgraphs)
        try:
            pagerank = nx.pagerank(G, max_iter=50)
        except Exception:
            pagerank = {}

        # Betweenness (only on small bounded subgraphs <= 300 nodes)
        if G.number_of_nodes() <= 300:
            try:
                betweenness = nx.betweenness_centrality(G, k=min(50, G.number_of_nodes()))
            except Exception:
                betweenness = {}
        else:
            betweenness = {}

        for node in G.nodes():
            metrics[node] = {
                "degree": degree.get(node, 0),
                "in_degree": in_degree.get(node, 0),
                "out_degree": out_degree.get(node, 0),
                "pagerank": round(pagerank.get(node, 0.0), 5),
                "betweenness": round(betweenness.get(node, 0.0), 5),
            }
    except Exception as e:
        logger.error(f"Error computing centrality: {e}")

    return metrics


def get_subgraph(db: Session, entity_type: str, entity_id: str, hops: int = 1, max_nodes: int = 100) -> dict:
    """
    Extract a bounded, memory-efficient k-hop subgraph around a specific entity.
    Queries database relationships directly — NEVER builds the full 100k graph in RAM.
    Returns Cytoscape.js compatible JSON format.
    """
    G = nx.DiGraph()
    center_key = f"{entity_type}:{entity_id}"
    G.add_node(center_key, type=entity_type, label=entity_id[:12] + "..." if len(entity_id) > 12 else entity_id, full_id=entity_id, is_center=True)

    visited_entities = {center_key}
    current_frontier = {(entity_type, entity_id)}

    for _ in range(min(hops, 2)):
        next_frontier = set()
        for e_type, e_id in current_frontier:
            if len(G.nodes) >= max_nodes:
                break

            if e_type == "WALLET":
                # 1. Look in GraphEdge
                edges = db.query(GraphEdge).filter(
                    (GraphEdge.source_id == e_id) | (GraphEdge.target_id == e_id)
                ).limit(30).all()
                for ge in edges:
                    s_node = f"{ge.source_type}:{ge.source_id}"
                    t_node = f"{ge.target_type}:{ge.target_id}"
                    G.add_node(s_node, type=ge.source_type, label=ge.source_id[:12] + "...", full_id=ge.source_id)
                    G.add_node(t_node, type=ge.target_type, label=ge.target_id[:12] + "...", full_id=ge.target_id)
                    G.add_edge(s_node, t_node, type=ge.edge_type, weight=ge.weight or 1.0, provenance=ge.provenance or "GraphEdge")
                    if s_node not in visited_entities:
                        visited_entities.add(s_node)
                        next_frontier.add((ge.source_type, ge.source_id))
                    if t_node not in visited_entities:
                        visited_entities.add(t_node)
                        next_frontier.add((ge.target_type, ge.target_id))

                # 2. Look in TransactionInput and TransactionOutput
                inps = db.query(TransactionInput).filter(TransactionInput.wallet_address == e_id).limit(20).all()
                for inp in inps:
                    tx = db.query(Transaction).filter(Transaction.id == inp.transaction_id).first()
                    if tx:
                        tx_node = f"TRANSACTION:{tx.txid}"
                        w_node = f"WALLET:{e_id}"
                        G.add_node(tx_node, type="TRANSACTION", label=tx.txid[:12] + "...", full_id=tx.txid)
                        G.add_edge(w_node, tx_node, type="INPUT_OF", amount=inp.amount or 0, provenance=f"input pos={inp.position}")
                        if tx_node not in visited_entities:
                            visited_entities.add(tx_node)
                            next_frontier.add(("TRANSACTION", tx.txid))

                outs = db.query(TransactionOutput).filter(TransactionOutput.wallet_address == e_id).limit(20).all()
                for out in outs:
                    tx = db.query(Transaction).filter(Transaction.id == out.transaction_id).first()
                    if tx:
                        tx_node = f"TRANSACTION:{tx.txid}"
                        w_node = f"WALLET:{e_id}"
                        G.add_node(tx_node, type="TRANSACTION", label=tx.txid[:12] + "...", full_id=tx.txid)
                        G.add_edge(tx_node, w_node, type="OUTPUT_OF", amount=out.amount or 0, provenance=f"output pos={out.position}")
                        if tx_node not in visited_entities:
                            visited_entities.add(tx_node)
                            next_frontier.add(("TRANSACTION", tx.txid))

            elif e_type == "TRANSACTION":
                # Look for inputs/outputs or edges
                edges = db.query(GraphEdge).filter(
                    (GraphEdge.source_id == e_id) | (GraphEdge.target_id == e_id)
                ).limit(30).all()
                for ge in edges:
                    s_node = f"{ge.source_type}:{ge.source_id}"
                    t_node = f"{ge.target_type}:{ge.target_id}"
                    G.add_node(s_node, type=ge.source_type, label=ge.source_id[:12] + "...", full_id=ge.source_id)
                    G.add_node(t_node, type=ge.target_type, label=ge.target_id[:12] + "...", full_id=ge.target_id)
                    G.add_edge(s_node, t_node, type=ge.edge_type, weight=ge.weight or 1.0, provenance=ge.provenance or "GraphEdge")

                # Network observations
                obs = db.query(NetworkObservation).filter(NetworkObservation.transaction_id == e_id).limit(10).all()
                for o in obs:
                    if o.src_ip:
                        ip_node = f"IP:{o.src_ip}"
                        tx_node = f"TRANSACTION:{e_id}"
                        G.add_node(ip_node, type="IP", label=o.src_ip, full_id=o.src_ip)
                        G.add_edge(ip_node, tx_node, type="OBSERVED_FROM", provenance="NetworkObservation")
                        if o.asn:
                            asn_node = f"ASN:{o.asn}"
                            G.add_node(asn_node, type="ASN", label=o.asn, full_id=o.asn)
                            G.add_edge(ip_node, asn_node, type="BELONGS_TO_ASN", provenance="NetworkObservation")

            elif e_type == "IP":
                obs = db.query(NetworkObservation).filter(NetworkObservation.src_ip == e_id).limit(30).all()
                for o in obs:
                    if o.transaction_id:
                        tx_node = f"TRANSACTION:{o.transaction_id}"
                        ip_node = f"IP:{e_id}"
                        G.add_node(tx_node, type="TRANSACTION", label=o.transaction_id[:12] + "...", full_id=o.transaction_id)
                        G.add_edge(ip_node, tx_node, type="OBSERVED_FROM", provenance="NetworkObservation")
                        if tx_node not in visited_entities:
                            visited_entities.add(tx_node)
                            next_frontier.add(("TRANSACTION", o.transaction_id))
                    if o.asn:
                        asn_node = f"ASN:{o.asn}"
                        ip_node = f"IP:{e_id}"
                        G.add_node(asn_node, type="ASN", label=o.asn, full_id=o.asn)
                        G.add_edge(ip_node, asn_node, type="BELONGS_TO_ASN", provenance="NetworkObservation")

        current_frontier = next_frontier

    # If the entity was not found anywhere, return empty graph
    if len(G.nodes) <= 1 and center_key in G and G.degree(center_key) == 0:
        exists = False
        if entity_type == "WALLET":
            exists = db.query(Wallet).filter(Wallet.address == entity_id).count() > 0
        elif entity_type == "TRANSACTION":
            exists = db.query(Transaction).filter(Transaction.txid == entity_id).count() > 0
        elif entity_type == "IP":
            exists = db.query(IPEntity).filter(IPEntity.ip_address == entity_id).count() > 0
        if not exists:
            return {"nodes": [], "edges": []}

    centrality = compute_centrality(G)

    nodes = []
    for node_id in G.nodes():
        data = dict(G.nodes[node_id])
        data["id"] = node_id
        data["centrality"] = centrality.get(node_id, {})
        data["is_center"] = (node_id == center_key)
        nodes.append({"data": data})

    edges = []
    for source, target in G.edges():
        edge_data = dict(G[source][target])
        edge_data["id"] = f"{source}->{target}"
        edge_data["source"] = source
        edge_data["target"] = target
        edges.append({"data": edge_data})

    return {
        "nodes": nodes,
        "edges": edges,
        "stats": {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "center_node": center_key,
            "hops": hops,
        }
    }


def get_path(db: Session, source_type: str, source_id: str,
             target_type: str, target_id: str) -> dict:
    """Find shortest path between two entities using bounded local BFS."""
    src_key = f"{source_type}:{source_id}"
    tgt_key = f"{target_type}:{target_id}"

    sub_src = get_subgraph(db, source_type, source_id, hops=2, max_nodes=50)
    sub_tgt = get_subgraph(db, target_type, target_id, hops=2, max_nodes=50)

    G = nx.DiGraph()
    for n in sub_src.get("nodes", []) + sub_tgt.get("nodes", []):
        G.add_node(n["data"]["id"], **n["data"])
    for e in sub_src.get("edges", []) + sub_tgt.get("edges", []):
        G.add_edge(e["data"]["source"], e["data"]["target"], **e["data"])

    if src_key not in G or tgt_key not in G:
        return {"path": [], "exists": False}

    try:
        path = nx.shortest_path(G, src_key, tgt_key)
        return {"path": path, "length": len(path) - 1, "exists": True}
    except nx.NetworkXNoPath:
        try:
            UG = G.to_undirected()
            path = nx.shortest_path(UG, src_key, tgt_key)
            return {"path": path, "length": len(path) - 1, "exists": True, "note": "Path found in undirected neighborhood"}
        except nx.NetworkXNoPath:
            return {"path": [], "exists": False}


def persist_graph(db: Session):
    """
    Safely persist graph metadata without blowing up memory.
    If GraphEdge already populated from relational bundle, preserve those edges.
    """
    existing_edge_count = db.query(GraphEdge.id).limit(1).count()
    if existing_edge_count > 0:
        logger.info(f"Graph edges already persisted in database. Bypassing redundant memory instantiation.")
        return

    G = build_graph(db, max_transactions=500)
    db.query(GraphNode).delete()

    node_batch = []
    for node_id in G.nodes():
        data = dict(G.nodes[node_id])
        node_type = data.get("type", "UNKNOWN")
        label = data.get("label", node_id)
        gn = GraphNode(node_type=node_type, node_id=node_id, label=label, properties=data)
        node_batch.append(gn)
        if len(node_batch) >= 1000:
            db.bulk_save_objects(node_batch)
            db.commit()
    if node_batch:
        db.bulk_save_objects(node_batch)
        db.commit()

    edge_batch = []
    for source, target in G.edges():
        edge_data = dict(G[source][target])
        edge_type = edge_data.get("type", "ASSOCIATED_WITH")
        ge = GraphEdge(
            source_type=source.split(":")[0] if ":" in source else "UNKNOWN",
            source_id=source.split(":", 1)[1] if ":" in source else source,
            target_type=target.split(":")[0] if ":" in target else "UNKNOWN",
            target_id=target.split(":", 1)[1] if ":" in target else target,
            edge_type=edge_type,
            weight=edge_data.get("amount", 1.0),
            properties=edge_data,
            provenance=edge_data.get("provenance", "derived"),
        )
        edge_batch.append(ge)
        if len(edge_batch) >= 1000:
            db.bulk_save_objects(edge_batch)
            db.commit()
            edge_batch = []
    if edge_batch:
        db.bulk_save_objects(edge_batch)
        db.commit()

    logger.info(f"Bounded graph persisted: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
