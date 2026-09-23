"""
BTC-SHIELD Graph Intelligence Service
Bounded NetworkX graph extraction, local centrality computation, on-demand ego subgraphs,
and Cytoscape.js-compatible JSON export.
Memory-Optimized: Zero full-graph in-memory instantiations for request-time queries.
Fully supports relational (Dataset 6), legacy, and audit-record schemas with prefix normalization.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String, func
import networkx as nx
from app.models.models import (
    Wallet, Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, IPEntity, ASNEntity, GraphNode, GraphEdge,
    AnomalyResult, RawRecord, Alert
)
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


def normalize_entity_key(entity_type: str, entity_id: str) -> tuple[str, str, str]:
    """
    Normalizes entity types and IDs, stripping redundant prefixes (e.g. 'WALLET:WALLET:xyz').
    Returns (clean_type, clean_id, canonical_key)
    Example: ('WALLET', '1aSnYkfg...', 'WALLET:1aSnYkfg...')
    """
    e_type = (entity_type or "WALLET").strip().upper()
    e_id = (entity_id or "").strip()

    # Repeatedly strip known prefixes if present in entity_id
    prefixes = [
        ("WALLET:", "WALLET"),
        ("TRANSACTION:", "TRANSACTION"),
        ("TX:", "TRANSACTION"),
        ("IP:", "IP"),
        ("ASN:", "ASN"),
        ("COUNTRY:", "COUNTRY")
    ]
    changed = True
    while changed:
        changed = False
        for prefix, inferred_type in prefixes:
            if e_id.upper().startswith(prefix):
                e_id = e_id[len(prefix):]
                if e_type in ["UNKNOWN", ""]:
                    e_type = inferred_type
                changed = True
                break

    if e_type in ["TX", "TRANSACTIONS"]:
        e_type = "TRANSACTION"
    elif e_type in ["WALLETS"]:
        e_type = "WALLET"
    elif e_type in ["IPS"]:
        e_type = "IP"
    elif e_type in ["ASNS"]:
        e_type = "ASN"

    return e_type, e_id, f"{e_type}:{e_id}"


def get_default_graph_entity(db: Session) -> dict:
    """
    Selects a highly-connected, high-priority entity to display when no entity is specified.
    Prioritizes top critical anomaly alert, then highest-degree active wallet.
    """
    # 1. Check for top CRITICAL alert with highest anomaly score
    top_alert = db.query(Alert).filter(Alert.priority == "CRITICAL").order_by(
        Alert.anomaly_score.desc().nullslast()
    ).first()
    if top_alert and top_alert.entity_id:
        e_type, e_id, _ = normalize_entity_key(top_alert.entity_type, top_alert.entity_id)
        return {"entity_type": e_type, "entity_id": e_id, "source": "CRITICAL_ALERT", "score": top_alert.anomaly_score}

    # 2. Check for wallet with highest transaction count
    top_wallet = db.query(Wallet).order_by(Wallet.tx_count.desc().nullslast()).first()
    if top_wallet and top_wallet.address:
        e_type, e_id, _ = normalize_entity_key("WALLET", top_wallet.address)
        return {"entity_type": e_type, "entity_id": e_id, "source": "TOP_WALLET", "tx_count": top_wallet.tx_count}

    # 3. Fallback to any alert
    any_alert = db.query(Alert).order_by(Alert.anomaly_score.desc().nullslast()).first()
    if any_alert and any_alert.entity_id:
        e_type, e_id, _ = normalize_entity_key(any_alert.entity_type, any_alert.entity_id)
        return {"entity_type": e_type, "entity_id": e_id, "source": "ANY_ALERT", "score": any_alert.anomaly_score}

    # 4. Fallback to any transaction
    any_tx = db.query(Transaction).first()
    if any_tx and any_tx.txid:
        return {"entity_type": "TRANSACTION", "entity_id": any_tx.txid, "source": "TRANSACTION"}

    return {"entity_type": "WALLET", "entity_id": "", "source": "NONE"}


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
    Normalizes prefixes, supports 100k relational graph edges, raw audit records, and network telemetry.
    Returns Cytoscape.js compatible JSON format.
    """
    e_type_clean, e_id_clean, center_key = normalize_entity_key(entity_type, entity_id)

    G = nx.DiGraph()
    G.add_node(
        center_key,
        type=e_type_clean,
        label=e_id_clean[:12] + "..." if len(e_id_clean) > 12 else e_id_clean,
        full_id=e_id_clean,
        is_center=True
    )

    # Scale max_nodes gracefully with hops
    effective_hops = max(1, min(hops, 3))
    if effective_hops == 1:
        node_limit = min(max_nodes, 100)
        edge_limit = 40
    elif effective_hops == 2:
        node_limit = min(max_nodes, 250)
        edge_limit = 70
    else:
        node_limit = min(max_nodes, 500)
        edge_limit = 100

    visited_entities = {center_key}
    current_frontier = {(e_type_clean, e_id_clean)}

    for _ in range(effective_hops):
        next_frontier = set()
        for curr_type, curr_id in current_frontier:
            if len(G.nodes) >= node_limit:
                break

            # ---------------------------------------------------------
            # 1. WALLET EXPANSION
            # ---------------------------------------------------------
            if curr_type == "WALLET":
                curr_node_key = f"WALLET:{curr_id}"

                # A. Query GraphEdge with direct source/target (with or without WALLET: prefix)
                direct_edges = db.query(GraphEdge).filter(
                    or_(
                        GraphEdge.source_id == curr_id,
                        GraphEdge.source_id == f"WALLET:{curr_id}",
                        GraphEdge.target_id == curr_id,
                        GraphEdge.target_id == f"WALLET:{curr_id}",
                    )
                ).limit(edge_limit).all()

                for ge in direct_edges:
                    s_type, s_id, s_key = normalize_entity_key(ge.source_type, ge.source_id)
                    t_type, t_id, t_key = normalize_entity_key(ge.target_type, ge.target_id)

                    if s_key not in G:
                        G.add_node(s_key, type=s_type, label=s_id[:12] + "...", full_id=s_id)
                    if t_key not in G:
                        G.add_node(t_key, type=t_type, label=t_id[:12] + "...", full_id=t_id)

                    G.add_edge(s_key, t_key, type=ge.edge_type or "ASSOCIATED_WITH", weight=ge.weight or 1.0, provenance=ge.provenance or "GraphEdge")

                    if s_key not in visited_entities and len(G.nodes) < node_limit:
                        visited_entities.add(s_key)
                        next_frontier.add((s_type, s_id))
                    if t_key not in visited_entities and len(G.nodes) < node_limit:
                        visited_entities.add(t_key)
                        next_frontier.add((t_type, t_id))

                # B. Query GraphEdge where wallet is in properties (Dataset 6 relational mode)
                if len(direct_edges) < 15:
                    prop_edges = db.query(GraphEdge).filter(
                        cast(GraphEdge.properties, String).like(f'%{curr_id}%')
                    ).limit(edge_limit).all()

                    connected_txids = []
                    for ge in prop_edges:
                        s_type, s_id, s_key = normalize_entity_key("TRANSACTION", ge.source_id)
                        t_type, t_id, t_key = normalize_entity_key("TRANSACTION", ge.target_id)

                        if s_key not in G:
                            G.add_node(s_key, type=s_type, label=s_id[:12] + "...", full_id=s_id)
                        if t_key not in G:
                            G.add_node(t_key, type=t_type, label=t_id[:12] + "...", full_id=t_id)

                        # Connect wallet into transaction money flow
                        G.add_edge(s_key, curr_node_key, type="OUTPUT_OF", weight=ge.weight or 1.0, provenance="Dataset6_Relational")
                        G.add_edge(curr_node_key, t_key, type="INPUT_OF", weight=ge.weight or 1.0, provenance="Dataset6_Relational")
                        G.add_edge(s_key, t_key, type=ge.edge_type or "MONEY_FLOW", weight=ge.weight or 1.0, provenance="Dataset6_Relational")

                        connected_txids.extend([s_id, t_id])

                        if s_key not in visited_entities and len(G.nodes) < node_limit:
                            visited_entities.add(s_key)
                            next_frontier.add((s_type, s_id))
                        if t_key not in visited_entities and len(G.nodes) < node_limit:
                            visited_entities.add(t_key)
                            next_frontier.add((t_type, t_id))

                    # Enrich connected transactions with network observations
                    if connected_txids:
                        obs = db.query(NetworkObservation).filter(
                            NetworkObservation.transaction_id.in_(connected_txids[:15])
                        ).all()
                        for o in obs:
                            if o.src_ip:
                                ip_type, ip_id, ip_key = normalize_entity_key("IP", o.src_ip)
                                tx_type, tx_id, tx_key = normalize_entity_key("TRANSACTION", o.transaction_id)
                                if ip_key not in G:
                                    G.add_node(ip_key, type=ip_type, label=ip_id, full_id=ip_id)
                                G.add_edge(ip_key, tx_key, type="OBSERVED_FROM", provenance="NetworkObservation")
                                if o.asn:
                                    asn_key = f"ASN:{o.asn}"
                                    if asn_key not in G:
                                        G.add_node(asn_key, type="ASN", label=o.asn, full_id=o.asn)
                                    G.add_edge(ip_key, asn_key, type="BELONGS_TO_ASN", provenance="NetworkObservation")

                # C. Query TransactionInput & TransactionOutput if present
                inps = db.query(TransactionInput).filter(TransactionInput.wallet_address == curr_id).limit(15).all()
                outs = db.query(TransactionOutput).filter(TransactionOutput.wallet_address == curr_id).limit(15).all()
                needed_tx_ids = set(inp.transaction_id for inp in inps if inp.transaction_id) | set(out.transaction_id for out in outs if out.transaction_id)
                if needed_tx_ids:
                    tx_map = {t.id: t for t in db.query(Transaction).filter(Transaction.id.in_(needed_tx_ids)).all()}
                    for inp in inps:
                        tx = tx_map.get(inp.transaction_id)
                        if tx:
                            _, tx_id, tx_key = normalize_entity_key("TRANSACTION", tx.txid)
                            if tx_key not in G:
                                G.add_node(tx_key, type="TRANSACTION", label=tx_id[:12] + "...", full_id=tx_id)
                            G.add_edge(curr_node_key, tx_key, type="INPUT_OF", amount=inp.amount or 0, provenance=f"pos={inp.position}")
                            if tx_key not in visited_entities and len(G.nodes) < node_limit:
                                visited_entities.add(tx_key)
                                next_frontier.add(("TRANSACTION", tx_id))

                    for out in outs:
                        tx = tx_map.get(out.transaction_id)
                        if tx:
                            _, tx_id, tx_key = normalize_entity_key("TRANSACTION", tx.txid)
                            if tx_key not in G:
                                G.add_node(tx_key, type="TRANSACTION", label=tx_id[:12] + "...", full_id=tx_id)
                            G.add_edge(tx_key, curr_node_key, type="OUTPUT_OF", amount=out.amount or 0, provenance=f"pos={out.position}")
                            if tx_key not in visited_entities and len(G.nodes) < node_limit:
                                visited_entities.add(tx_key)
                                next_frontier.add(("TRANSACTION", tx_id))

                # D. Fallback to RawRecord if still isolated
                if G.degree(curr_node_key) == 0:
                    raws = db.query(RawRecord).filter(
                        cast(RawRecord.raw_data, String).like(f'%{curr_id}%')
                    ).limit(10).all()
                    for r in raws:
                        if isinstance(r.raw_data, dict):
                            txid = r.raw_data.get("txid")
                            if not txid:
                                continue
                            _, tx_id, tx_key = normalize_entity_key("TRANSACTION", txid)
                            if tx_key not in G:
                                G.add_node(tx_key, type="TRANSACTION", label=tx_id[:12] + "...", full_id=tx_id)

                            in_addrs = str(r.raw_data.get("input_addresses", "")).split(";")
                            out_addrs = str(r.raw_data.get("output_addresses", "")).split(";")

                            if curr_id in in_addrs:
                                G.add_edge(curr_node_key, tx_key, type="INPUT_OF", provenance="RawRecord")
                            if curr_id in out_addrs:
                                G.add_edge(tx_key, curr_node_key, type="OUTPUT_OF", provenance="RawRecord")

                            # Add counterparties (up to 3)
                            for cp in [a for a in out_addrs if a and a != curr_id][:3]:
                                cp_key = f"WALLET:{cp}"
                                if cp_key not in G:
                                    G.add_node(cp_key, type="WALLET", label=cp[:12] + "...", full_id=cp)
                                G.add_edge(tx_key, cp_key, type="OUTPUT_OF", provenance="RawRecord")

                            # Add network telemetry
                            src_ip = r.raw_data.get("src_ip")
                            if src_ip:
                                ip_key = f"IP:{src_ip}"
                                if ip_key not in G:
                                    G.add_node(ip_key, type="IP", label=src_ip, full_id=src_ip)
                                G.add_edge(ip_key, tx_key, type="OBSERVED_FROM", provenance="RawRecord")
                                asn = r.raw_data.get("asn")
                                if asn:
                                    asn_key = f"ASN:{asn}"
                                    if asn_key not in G:
                                        G.add_node(asn_key, type="ASN", label=asn, full_id=asn)
                                    G.add_edge(ip_key, asn_key, type="BELONGS_TO_ASN", provenance="RawRecord")

                            if tx_key not in visited_entities and len(G.nodes) < node_limit:
                                visited_entities.add(tx_key)
                                next_frontier.add(("TRANSACTION", tx_id))

            # ---------------------------------------------------------
            # 2. TRANSACTION EXPANSION
            # ---------------------------------------------------------
            elif curr_type == "TRANSACTION":
                curr_node_key = f"TRANSACTION:{curr_id}"

                # Direct GraphEdges
                edges = db.query(GraphEdge).filter(
                    or_(
                        GraphEdge.source_id == curr_id,
                        GraphEdge.source_id == f"TX:{curr_id}",
                        GraphEdge.source_id == f"TRANSACTION:{curr_id}",
                        GraphEdge.target_id == curr_id,
                        GraphEdge.target_id == f"TX:{curr_id}",
                        GraphEdge.target_id == f"TRANSACTION:{curr_id}",
                    )
                ).limit(edge_limit).all()

                for ge in edges:
                    s_type, s_id, s_key = normalize_entity_key(ge.source_type, ge.source_id)
                    t_type, t_id, t_key = normalize_entity_key(ge.target_type, ge.target_id)

                    if s_key not in G:
                        G.add_node(s_key, type=s_type, label=s_id[:12] + "...", full_id=s_id)
                    if t_key not in G:
                        G.add_node(t_key, type=t_type, label=t_id[:12] + "...", full_id=t_id)

                    G.add_edge(s_key, t_key, type=ge.edge_type or "MONEY_FLOW", weight=ge.weight or 1.0, provenance=ge.provenance or "GraphEdge")

                    # If property contains wallet_address, connect it
                    if isinstance(ge.properties, dict) and ge.properties.get("wallet_address"):
                        w_addr = ge.properties["wallet_address"]
                        w_key = f"WALLET:{w_addr}"
                        if w_key not in G:
                            G.add_node(w_key, type="WALLET", label=w_addr[:12] + "...", full_id=w_addr)
                        G.add_edge(s_key, w_key, type="OUTPUT_OF", provenance="GraphEdge")
                        G.add_edge(w_key, t_key, type="INPUT_OF", provenance="GraphEdge")

                    if s_key not in visited_entities and len(G.nodes) < node_limit:
                        visited_entities.add(s_key)
                        next_frontier.add((s_type, s_id))
                    if t_key not in visited_entities and len(G.nodes) < node_limit:
                        visited_entities.add(t_key)
                        next_frontier.add((t_type, t_id))

                # Network observations for this transaction
                obs = db.query(NetworkObservation).filter(NetworkObservation.transaction_id == curr_id).limit(10).all()
                for o in obs:
                    if o.src_ip:
                        ip_key = f"IP:{o.src_ip}"
                        if ip_key not in G:
                            G.add_node(ip_key, type="IP", label=o.src_ip, full_id=o.src_ip)
                        G.add_edge(ip_key, curr_node_key, type="OBSERVED_FROM", provenance="NetworkObservation")
                        if o.asn:
                            asn_key = f"ASN:{o.asn}"
                            if asn_key not in G:
                                G.add_node(asn_key, type="ASN", label=o.asn, full_id=o.asn)
                            G.add_edge(ip_key, asn_key, type="BELONGS_TO_ASN", provenance="NetworkObservation")

                # If no edges, fallback to RawRecord
                if G.degree(curr_node_key) == 0:
                    raw = db.query(RawRecord).filter(
                        cast(RawRecord.raw_data, String).like(f'%{curr_id}%')
                    ).first()
                    if raw and isinstance(raw.raw_data, dict):
                        in_addrs = str(raw.raw_data.get("input_addresses", "")).split(";")
                        out_addrs = str(raw.raw_data.get("output_addresses", "")).split(";")
                        for inp in [a for a in in_addrs if a][:5]:
                            inp_key = f"WALLET:{inp}"
                            if inp_key not in G:
                                G.add_node(inp_key, type="WALLET", label=inp[:12] + "...", full_id=inp)
                            G.add_edge(inp_key, curr_node_key, type="INPUT_OF", provenance="RawRecord")
                        for out in [a for a in out_addrs if a][:5]:
                            out_key = f"WALLET:{out}"
                            if out_key not in G:
                                G.add_node(out_key, type="WALLET", label=out[:12] + "...", full_id=out)
                            G.add_edge(curr_node_key, out_key, type="OUTPUT_OF", provenance="RawRecord")

            # ---------------------------------------------------------
            # 3. IP EXPANSION
            # ---------------------------------------------------------
            elif curr_type == "IP":
                curr_node_key = f"IP:{curr_id}"
                obs = db.query(NetworkObservation).filter(
                    or_(NetworkObservation.src_ip == curr_id, NetworkObservation.dst_ip == curr_id)
                ).limit(30).all()

                for o in obs:
                    if o.transaction_id:
                        _, tx_id, tx_key = normalize_entity_key("TRANSACTION", o.transaction_id)
                        if tx_key not in G:
                            G.add_node(tx_key, type="TRANSACTION", label=tx_id[:12] + "...", full_id=tx_id)
                        G.add_edge(curr_node_key, tx_key, type="OBSERVED_FROM", provenance="NetworkObservation")
                        if tx_key not in visited_entities and len(G.nodes) < node_limit:
                            visited_entities.add(tx_key)
                            next_frontier.add(("TRANSACTION", tx_id))
                    if o.asn:
                        asn_key = f"ASN:{o.asn}"
                        if asn_key not in G:
                            G.add_node(asn_key, type="ASN", label=o.asn, full_id=o.asn)
                        G.add_edge(curr_node_key, asn_key, type="BELONGS_TO_ASN", provenance="NetworkObservation")

            # ---------------------------------------------------------
            # 4. ASN EXPANSION
            # ---------------------------------------------------------
            elif curr_type == "ASN":
                curr_node_key = f"ASN:{curr_id}"
                obs = db.query(NetworkObservation).filter(NetworkObservation.asn == curr_id).limit(30).all()
                for o in obs:
                    if o.src_ip:
                        ip_key = f"IP:{o.src_ip}"
                        if ip_key not in G:
                            G.add_node(ip_key, type="IP", label=o.src_ip, full_id=o.src_ip)
                        G.add_edge(ip_key, curr_node_key, type="BELONGS_TO_ASN", provenance="NetworkObservation")
                        if ip_key not in visited_entities and len(G.nodes) < node_limit:
                            visited_entities.add(ip_key)
                            next_frontier.add(("IP", o.src_ip))

        current_frontier = next_frontier

    # Verify if center entity exists in database even if completely isolated
    if len(G.nodes) <= 1 and center_key in G and G.degree(center_key) == 0:
        exists = False
        if e_type_clean == "WALLET":
            exists = db.query(Wallet.id).filter(Wallet.address == e_id_clean).first() is not None
        elif e_type_clean == "TRANSACTION":
            exists = db.query(Transaction.id).filter(Transaction.txid == e_id_clean).first() is not None
        elif e_type_clean == "IP":
            exists = db.query(IPEntity.id).filter(IPEntity.ip_address == e_id_clean).first() is not None
        if not exists:
            # Check if mentioned in raw_records or alerts
            exists = (
                db.query(Alert.id).filter(Alert.entity_id == e_id_clean).first() is not None or
                db.query(RawRecord.id).filter(cast(RawRecord.raw_data, String).like(f'%{e_id_clean}%')).first() is not None
            )
        if not exists:
            return {"nodes": [], "edges": [], "stats": {"node_count": 0, "edge_count": 0, "center_node": center_key, "hops": hops, "is_isolated": True}}

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
            "is_isolated": len(edges) == 0
        }
    }


def get_path(db: Session, source_type: str, source_id: str,
             target_type: str, target_id: str) -> dict:
    """Find shortest path between two entities using bounded local BFS."""
    _, s_id, src_key = normalize_entity_key(source_type, source_id)
    _, t_id, tgt_key = normalize_entity_key(target_type, target_id)

    sub_src = get_subgraph(db, source_type, s_id, hops=2, max_nodes=50)
    sub_tgt = get_subgraph(db, target_type, t_id, hops=2, max_nodes=50)

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
        logger.info("Graph edges already persisted in database. Bypassing redundant memory instantiation.")
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
        s_type, s_id, _ = normalize_entity_key("UNKNOWN", source)
        t_type, t_id, _ = normalize_entity_key("UNKNOWN", target)
        ge = GraphEdge(
            source_type=s_type,
            source_id=s_id,
            target_type=t_type,
            target_id=t_id,
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
