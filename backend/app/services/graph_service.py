"""
BTC-SHIELD Graph Intelligence Service
NetworkX-based graph construction, centrality computation, subgraph extraction,
and Cytoscape.js-compatible JSON export.
"""
from sqlalchemy.orm import Session
import networkx as nx
from app.models.models import (
    Wallet, Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, IPEntity, ASNEntity, GraphNode, GraphEdge,
    AnomalyResult
)
import logging

logger = logging.getLogger(__name__)


def build_graph(db: Session) -> nx.DiGraph:
    """
    Construct a directed multigraph from all entities and their relationships.
    Node types: WALLET, TRANSACTION, IP, ASN, COUNTRY
    Edge types: INPUT_OF, OUTPUT_OF, OBSERVED_FROM, LOCATED_IN, BELONGS_TO_ASN, COUNTERPARTY
    """
    G = nx.DiGraph()

    # --- Add Wallet nodes ---
    wallets = db.query(Wallet).all()
    for w in wallets:
        anomaly = db.query(AnomalyResult).filter(
            AnomalyResult.entity_type == "WALLET",
            AnomalyResult.entity_id == w.address
        ).order_by(AnomalyResult.created_at.desc()).first()

        G.add_node(f"WALLET:{w.address}", **{
            "type": "WALLET",
            "label": w.address[:12] + "..." if len(w.address) > 12 else w.address,
            "full_id": w.address,
            "tx_count": w.tx_count or 0,
            "total_sent": w.total_sent or 0,
            "total_received": w.total_received or 0,
            "anomaly_score": anomaly.anomaly_score if anomaly else None,
        })

    # --- Add Transaction nodes and edges ---
    transactions = db.query(Transaction).all()
    for tx in transactions:
        G.add_node(f"TX:{tx.txid}", **{
            "type": "TRANSACTION",
            "label": tx.txid[:12] + "...",
            "full_id": tx.txid,
            "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
            "fee": tx.fee,
            "total_input": tx.total_input,
            "total_output": tx.total_output,
        })

        # Input edges: WALLET -> TRANSACTION
        inputs = db.query(TransactionInput).filter(
            TransactionInput.transaction_id == tx.id
        ).all()
        for inp in inputs:
            wallet_node = f"WALLET:{inp.wallet_address}"
            tx_node = f"TX:{tx.txid}"
            if wallet_node in G:
                G.add_edge(wallet_node, tx_node, **{
                    "type": "INPUT_OF",
                    "amount": inp.amount or 0,
                    "provenance": f"TransactionInput position={inp.position}",
                })

        # Output edges: TRANSACTION -> WALLET
        outputs = db.query(TransactionOutput).filter(
            TransactionOutput.transaction_id == tx.id
        ).all()
        for out in outputs:
            wallet_node = f"WALLET:{out.wallet_address}"
            tx_node = f"TX:{tx.txid}"
            if wallet_node in G:
                G.add_edge(tx_node, wallet_node, **{
                    "type": "OUTPUT_OF",
                    "amount": out.amount or 0,
                    "provenance": f"TransactionOutput position={out.position}",
                })

        # Counterparty edges: Input wallet -> Output wallet (direct link)
        input_addrs = set(inp.wallet_address for inp in inputs)
        output_addrs = set(out.wallet_address for out in outputs)
        for in_addr in input_addrs:
            for out_addr in output_addrs:
                if in_addr != out_addr:
                    src = f"WALLET:{in_addr}"
                    tgt = f"WALLET:{out_addr}"
                    if src in G and tgt in G:
                        if not G.has_edge(src, tgt):
                            G.add_edge(src, tgt, **{
                                "type": "COUNTERPARTY",
                                "tx_count": 1,
                                "provenance": f"via TX {tx.txid[:12]}",
                            })
                        else:
                            edge_data = G[src][tgt]
                            edge_data["tx_count"] = edge_data.get("tx_count", 0) + 1

    # --- Add IP nodes and edges ---
    ip_entities = db.query(IPEntity).all()
    for ip_ent in ip_entities:
        G.add_node(f"IP:{ip_ent.ip_address}", **{
            "type": "IP",
            "label": ip_ent.ip_address,
            "full_id": ip_ent.ip_address,
            "observation_count": ip_ent.observation_count or 0,
            "country": ip_ent.country or "",
            "asn": ip_ent.asn or "",
        })

    # --- Add ASN nodes ---
    asn_entities = db.query(ASNEntity).all()
    for asn_ent in asn_entities:
        G.add_node(f"ASN:{asn_ent.asn_number}", **{
            "type": "ASN",
            "label": asn_ent.asn_number,
            "full_id": asn_ent.asn_number,
            "ip_count": asn_ent.ip_count or 0,
        })

    # --- Network observation edges ---
    observations = db.query(NetworkObservation).all()
    countries_seen = set()
    for obs in observations:
        tx_node = f"TX:{obs.transaction_id}"
        ip_node = f"IP:{obs.src_ip}"

        # TX observed from IP
        if tx_node in G and ip_node in G:
            if not G.has_edge(ip_node, tx_node):
                G.add_edge(ip_node, tx_node, **{
                    "type": "OBSERVED_FROM",
                    "timestamp": obs.timestamp.isoformat() if obs.timestamp else None,
                    "provenance": "NetworkObservation",
                })

        # IP belongs to ASN
        if obs.asn:
            asn_node = f"ASN:{obs.asn}"
            if ip_node in G and asn_node in G:
                if not G.has_edge(ip_node, asn_node):
                    G.add_edge(ip_node, asn_node, **{
                        "type": "BELONGS_TO_ASN",
                        "provenance": "NetworkObservation ASN field",
                    })

        # IP located in country
        if obs.geo_country:
            country_node = f"COUNTRY:{obs.geo_country}"
            if country_node not in G:
                G.add_node(country_node, **{
                    "type": "COUNTRY",
                    "label": obs.geo_country,
                    "full_id": obs.geo_country,
                })
                countries_seen.add(obs.geo_country)
            if ip_node in G and not G.has_edge(ip_node, country_node):
                G.add_edge(ip_node, country_node, **{
                    "type": "LOCATED_IN",
                    "provenance": "NetworkObservation geo_country",
                })

    logger.info(
        f"Graph built: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges"
    )
    return G


def compute_centrality(G: nx.DiGraph) -> dict:
    """Compute graph centrality metrics."""
    metrics = {}
    if G.number_of_nodes() == 0:
        return metrics

    try:
        degree = dict(G.degree())
        in_degree = dict(G.in_degree())
        out_degree = dict(G.out_degree())

        # PageRank
        try:
            pagerank = nx.pagerank(G, max_iter=100)
        except Exception:
            pagerank = {}

        # Betweenness (can be expensive, limit for large graphs)
        if G.number_of_nodes() <= 5000:
            try:
                betweenness = nx.betweenness_centrality(G, k=min(100, G.number_of_nodes()))
            except Exception:
                betweenness = {}
        else:
            betweenness = {}

        for node in G.nodes():
            metrics[node] = {
                "degree": degree.get(node, 0),
                "in_degree": in_degree.get(node, 0),
                "out_degree": out_degree.get(node, 0),
                "pagerank": pagerank.get(node, 0),
                "betweenness": betweenness.get(node, 0),
            }
    except Exception as e:
        logger.error(f"Error computing centrality: {e}")

    return metrics


def get_subgraph(db: Session, entity_type: str, entity_id: str, hops: int = 1) -> dict:
    """
    Extract a k-hop subgraph around a specific entity.
    Returns Cytoscape.js compatible JSON format.
    """
    G = build_graph(db)

    node_key = f"{entity_type}:{entity_id}"
    if node_key not in G:
        return {"nodes": [], "edges": []}

    # BFS to get k-hop neighborhood
    visited = {node_key}
    frontier = {node_key}

    for _ in range(hops):
        next_frontier = set()
        for node in frontier:
            # Successors
            for neighbor in G.successors(node):
                if neighbor not in visited:
                    next_frontier.add(neighbor)
                    visited.add(neighbor)
            # Predecessors
            for neighbor in G.predecessors(node):
                if neighbor not in visited:
                    next_frontier.add(neighbor)
                    visited.add(neighbor)
        frontier = next_frontier

    # Extract subgraph
    subgraph = G.subgraph(visited)

    # Compute centrality for the subgraph
    centrality = compute_centrality(subgraph)

    # Convert to Cytoscape.js format
    nodes = []
    for node_id in subgraph.nodes():
        data = dict(subgraph.nodes[node_id])
        data["id"] = node_id
        data["centrality"] = centrality.get(node_id, {})
        data["is_center"] = (node_id == node_key)
        nodes.append({"data": data})

    edges = []
    for source, target in subgraph.edges():
        edge_data = dict(subgraph[source][target])
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
            "center_node": node_key,
            "hops": hops,
        }
    }


def get_path(db: Session, source_type: str, source_id: str,
             target_type: str, target_id: str) -> dict:
    """Find shortest path between two entities."""
    G = build_graph(db)

    src_key = f"{source_type}:{source_id}"
    tgt_key = f"{target_type}:{target_id}"

    if src_key not in G or tgt_key not in G:
        return {"path": [], "exists": False}

    try:
        path = nx.shortest_path(G, src_key, tgt_key)
        return {
            "path": path,
            "length": len(path) - 1,
            "exists": True,
        }
    except nx.NetworkXNoPath:
        # Try undirected
        try:
            UG = G.to_undirected()
            path = nx.shortest_path(UG, src_key, tgt_key)
            return {
                "path": path,
                "length": len(path) - 1,
                "exists": True,
                "note": "Path found in undirected graph",
            }
        except nx.NetworkXNoPath:
            return {"path": [], "exists": False}


def persist_graph(db: Session):
    """Persist graph nodes and edges to database for fast retrieval."""
    G = build_graph(db)

    # Clear existing graph data
    db.query(GraphEdge).delete()
    db.query(GraphNode).delete()

    centrality = compute_centrality(G)

    for node_id in G.nodes():
        data = dict(G.nodes[node_id])
        node_type = data.get("type", "UNKNOWN")
        label = data.get("label", node_id)

        data["centrality"] = centrality.get(node_id, {})

        gn = GraphNode(
            node_type=node_type,
            node_id=node_id,
            label=label,
            properties=data,
        )
        db.add(gn)

    for source, target in G.edges():
        edge_data = dict(G[source][target])
        edge_type = edge_data.get("type", "ASSOCIATED_WITH")

        ge = GraphEdge(
            source_type=source.split(":")[0] if ":" in source else "UNKNOWN",
            source_id=source,
            target_type=target.split(":")[0] if ":" in target else "UNKNOWN",
            target_id=target,
            edge_type=edge_type,
            weight=edge_data.get("amount", 1.0),
            properties=edge_data,
            provenance=edge_data.get("provenance", "derived"),
        )
        db.add(ge)

    db.commit()
    logger.info(f"Graph persisted: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
