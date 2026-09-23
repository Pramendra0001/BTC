"""
BTC-SHIELD Structural Heuristics Service
Detects peeling chains, CoinJoin/mixing patterns, and high fan-in/fan-out topologies.
"""
from sqlalchemy.orm import Session
from app.models.models import Transaction, TransactionInput, TransactionOutput, Wallet
from collections import defaultdict
from datetime import datetime
import math
import logging

logger = logging.getLogger(__name__)

def compute_entropy(values: list[float]) -> float:
    """Compute Shannon entropy of a distribution of values."""
    if not values:
        return 0.0
    total = sum(values)
    if total <= 0:
        return 0.0
    probs = [v / total for v in values if v > 0]
    return -sum(p * math.log2(p) for p in probs)

def detect_peeling_chains(db: Session, min_hops: int = 2, limit: int = 50) -> list[dict]:
    """
    Detect peeling chains across transactions.
    A peeling chain is a sequential cascade where each step has:
    - 1 or 2 inputs
    - 2 outputs (one peel payment, one change output that continues the chain)
    - Output asymmetry where one output is peeled and the remainder forms the change.
    """
    # Bounded query: Inspect most recent transactions to prevent out-of-memory and 30s hangs on 100k datasets
    txs = db.query(Transaction).order_by(Transaction.timestamp.desc().nullslast()).limit(2000).all()
    if not txs:
        return []

    tx_by_id = {tx.id: tx for tx in txs}
    tx_by_txid = {tx.txid: tx for tx in txs}
    tx_ids = [tx.id for tx in txs]
    
    inputs_by_tx = defaultdict(list)
    outputs_by_tx = defaultdict(list)
    
    if tx_ids:
        for inp in db.query(TransactionInput).filter(TransactionInput.transaction_id.in_(tx_ids)).all():
            inputs_by_tx[inp.transaction_id].append(inp)
        for out in db.query(TransactionOutput).filter(TransactionOutput.transaction_id.in_(tx_ids)).all():
            outputs_by_tx[out.transaction_id].append(out)

    # Candidate 2-output transactions
    candidate_txids = set()
    spending_map = defaultdict(list) # wallet_address -> list of txs where this wallet spent
    
    for tx_id, inps in inputs_by_tx.items():
        tx = tx_by_id.get(tx_id)
        if not tx:
            continue
        for inp in inps:
            if inp.wallet_address:
                spending_map[inp.wallet_address].append(tx)

    for tx in txs:
        outs = outputs_by_tx.get(tx.id, [])
        inps = inputs_by_tx.get(tx.id, [])
        if len(outs) == 2 and 1 <= len(inps) <= 2:
            candidate_txids.add(tx.txid)

    visited_txids = set()
    chains = []

    # Sort candidate transactions chronologically
    sorted_candidates = sorted(
        [tx_by_txid[t] for t in candidate_txids if t in tx_by_txid and tx_by_txid[t].timestamp],
        key=lambda x: x.timestamp
    )

    for start_tx in sorted_candidates:
        if start_tx.txid in visited_txids:
            continue

        current_tx = start_tx
        current_chain_hops = []
        chain_addresses = set()
        total_peeled = 0.0

        while current_tx:
            visited_txids.add(current_tx.txid)
            outs = outputs_by_tx.get(current_tx.id, [])
            if len(outs) != 2:
                break

            out1, out2 = outs[0], outs[1]
            # Identify peeled vs change: typically change is the larger or unspent, peeled is smaller
            # If amounts are unequal, assume smaller is peeled payment, larger is change
            if out1.amount <= out2.amount:
                peel_out = out1
                change_out = out2
            else:
                peel_out = out2
                change_out = out1

            total_peeled += peel_out.amount
            chain_addresses.add(peel_out.wallet_address)
            chain_addresses.add(change_out.wallet_address)

            current_chain_hops.append({
                "hop": len(current_chain_hops) + 1,
                "txid": current_tx.txid,
                "timestamp": current_tx.timestamp.isoformat() if current_tx.timestamp else None,
                "peeled_amount": round(peel_out.amount, 6),
                "peeled_address": peel_out.wallet_address,
                "change_amount": round(change_out.amount, 6),
                "change_address": change_out.wallet_address,
                "fee": current_tx.fee or 0.0,
            })

            # Check if change_out was subsequently spent in another candidate 2-output transaction
            next_tx = None
            if change_out.wallet_address in spending_map:
                possible_spends = [
                    sp for sp in spending_map[change_out.wallet_address]
                    if sp.txid != current_tx.txid
                    and sp.txid in candidate_txids
                    and (not current_tx.timestamp or not sp.timestamp or sp.timestamp >= current_tx.timestamp)
                ]
                if possible_spends:
                    # Pick earliest subsequent spend
                    possible_spends.sort(key=lambda x: x.timestamp if x.timestamp else datetime.min)
                    next_tx = possible_spends[0]

            if next_tx and next_tx.txid not in visited_txids:
                current_tx = next_tx
            else:
                break

        if len(current_chain_hops) >= min_hops:
            initial_balance = current_chain_hops[0]["peeled_amount"] + current_chain_hops[0]["change_amount"]
            last_hop = current_chain_hops[-1]
            chains.append({
                "chain_id": f"peel_{start_tx.txid[:10]}",
                "start_txid": start_tx.txid,
                "terminal_txid": last_hop["txid"],
                "hop_count": len(current_chain_hops),
                "total_peeled_btc": round(total_peeled, 6),
                "initial_amount_btc": round(initial_balance, 6),
                "final_change_btc": round(last_hop["change_amount"], 6),
                "unique_addresses_count": len(chain_addresses),
                "confidence_score": min(95.0, 50.0 + (len(current_chain_hops) * 12.0)),
                "hops": current_chain_hops
            })
            if len(chains) >= limit:
                break

    chains.sort(key=lambda c: (c["hop_count"], c["total_peeled_btc"]), reverse=True)
    return chains

def detect_mixing_patterns(db: Session, limit: int = 50) -> list[dict]:
    """
    Detect CoinJoin and mixing/tumbling patterns.
    Indicators:
    1. Equal output values (standard CoinJoin fingerprint e.g. 0.1 BTC, 0.05 BTC).
    2. High input count + high output count (many-to-many topology).
    3. Output entropy profile (uniform distribution across participants).
    """
    # Bounded query: Inspect most recent transactions to prevent out-of-memory and 30s hangs on 100k datasets
    txs = db.query(Transaction).order_by(Transaction.timestamp.desc().nullslast()).limit(2000).all()
    if not txs:
        return []

    outputs_by_tx = defaultdict(list)
    inputs_by_tx = defaultdict(list)
    tx_ids = [tx.id for tx in txs]

    if tx_ids:
        for out in db.query(TransactionOutput).filter(TransactionOutput.transaction_id.in_(tx_ids)).all():
            outputs_by_tx[out.transaction_id].append(out)
        for inp in db.query(TransactionInput).filter(TransactionInput.transaction_id.in_(tx_ids)).all():
            inputs_by_tx[inp.transaction_id].append(inp)

    mix_records = []

    for tx in txs:
        outs = outputs_by_tx.get(tx.id, [])
        inps = inputs_by_tx.get(tx.id, [])

        if len(outs) < 2:
            continue

        # Group output amounts rounded to 6 decimal places
        amount_groups = defaultdict(list)
        out_amounts = []
        for o in outs:
            amt_rounded = round(o.amount, 6)
            amount_groups[amt_rounded].append(o.wallet_address)
            out_amounts.append(o.amount)

        # Find largest cluster of identical outputs
        equal_clusters = {amt: addrs for amt, addrs in amount_groups.items() if len(addrs) >= 2}
        max_equal_count = max([len(addrs) for addrs in amount_groups.values()], default=0)

        entropy = compute_entropy(out_amounts)
        input_count = len(inps)
        output_count = len(outs)

        is_coinjoin = False
        is_tumbler = False
        mix_type = "STANDARD"
        confidence = 0.0

        # Heuristic 1: CoinJoin Equal Denomination (e.g. 3+ outputs of exact same amount)
        if max_equal_count >= 3:
            is_coinjoin = True
            mix_type = "EQUAL_DENOMINATION_COINJOIN"
            confidence = min(98.0, 60.0 + (max_equal_count * 8.0))
        elif max_equal_count == 2 and input_count >= 3:
            is_coinjoin = True
            mix_type = "PARTIAL_DENOMINATION_COINJOIN"
            confidence = 65.0
        # Heuristic 2: Many-to-Many Multi-Party Tumbler
        elif input_count >= 4 and output_count >= 4:
            is_tumbler = True
            mix_type = "MANY_TO_MANY_TUMBLER"
            confidence = min(90.0, 50.0 + ((input_count + output_count) * 3.0))
        # Heuristic 3: High Fan-Out Dispersion (1 to 6+)
        elif input_count == 1 and output_count >= 6:
            mix_type = "HIGH_FAN_OUT_DISPERSION"
            confidence = min(85.0, 45.0 + (output_count * 4.0))

        if is_coinjoin or is_tumbler or mix_type != "STANDARD":
            mix_records.append({
                "txid": tx.txid,
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "pattern_type": mix_type,
                "confidence_score": round(confidence, 1),
                "input_count": input_count,
                "output_count": output_count,
                "max_equal_outputs": max_equal_count,
                "equal_denominations": [
                    {"amount_btc": amt, "count": len(addrs)}
                    for amt, addrs in equal_clusters.items()
                ],
                "entropy_bits": round(entropy, 3),
                "total_volume_btc": round(tx.total_output or 0.0, 6),
                "fee_btc": round(tx.fee or 0.0, 6)
            })

    mix_records.sort(key=lambda m: (m["confidence_score"], m["output_count"]), reverse=True)
    return mix_records[:limit]

def analyze_transaction_heuristics(db: Session, txid: str) -> dict:
    """Analyze single transaction for peeling, mixing, and fan-out/fan-in structures."""
    tx = db.query(Transaction).filter(Transaction.txid == txid).first()
    if not tx:
        return {"found": False, "message": "Transaction not found"}

    inps = db.query(TransactionInput).filter(TransactionInput.transaction_id == tx.id).all()
    outs = db.query(TransactionOutput).filter(TransactionOutput.transaction_id == tx.id).all()

    in_count = len(inps)
    out_count = len(outs)
    amounts = [o.amount for o in outs]
    entropy = compute_entropy(amounts)

    # Equal amounts analysis
    amt_counts = defaultdict(int)
    for a in amounts:
        amt_counts[round(a, 6)] += 1
    max_equal = max(amt_counts.values(), default=0)

    # Peeling signature check
    is_peeling_candidate = False
    asymmetry_ratio = 0.0
    if out_count == 2 and 1 <= in_count <= 2:
        is_peeling_candidate = True
        min_a = min(amounts)
        max_a = max(amounts) if max(amounts) > 0 else 1.0
        asymmetry_ratio = min_a / max_a

    detected_patterns = []
    if max_equal >= 3:
        detected_patterns.append("COINJOIN_EQUAL_OUTPUTS")
    if in_count >= 4 and out_count >= 4:
        detected_patterns.append("MANY_TO_MANY_TUMBLER")
    if in_count == 1 and out_count >= 5:
        detected_patterns.append("FAN_OUT_DISPERSION")
    if in_count >= 5 and out_count == 1:
        detected_patterns.append("FAN_IN_CONSOLIDATION")
    if is_peeling_candidate and asymmetry_ratio < 0.4:
        detected_patterns.append("PEELING_CHAIN_STEP")

    return {
        "found": True,
        "txid": tx.txid,
        "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
        "input_count": in_count,
        "output_count": out_count,
        "total_volume_btc": round(tx.total_output or 0.0, 6),
        "fee_btc": round(tx.fee or 0.0, 6),
        "entropy_bits": round(entropy, 3),
        "max_equal_outputs": max_equal,
        "is_peeling_candidate": is_peeling_candidate,
        "asymmetry_ratio": round(asymmetry_ratio, 3),
        "detected_patterns": detected_patterns or ["STANDARD_TRANSFER"],
        "structural_risk_level": "HIGH" if any(p in ["COINJOIN_EQUAL_OUTPUTS", "MANY_TO_MANY_TUMBLER", "PEELING_CHAIN_STEP"] for p in detected_patterns) else "LOW"
    }

def get_heuristics_summary(db: Session) -> dict:
    """Get high-level summary of structural patterns across the database."""
    peeling = detect_peeling_chains(db, min_hops=2, limit=100)
    mixing = detect_mixing_patterns(db, limit=100)

    total_peeled_volume = sum(p["total_peeled_btc"] for p in peeling)
    total_mixing_volume = sum(m["total_volume_btc"] for m in mixing)

    return {
        "peeling_chains_detected": len(peeling),
        "total_peeled_volume_btc": round(total_peeled_volume, 6),
        "max_chain_hops": max([p["hop_count"] for p in peeling], default=0),
        "mixing_transactions_detected": len(mixing),
        "total_mixing_volume_btc": round(total_mixing_volume, 6),
        "coinjoin_rounds_count": len([m for m in mixing if "COINJOIN" in m["pattern_type"]]),
        "tumbler_transactions_count": len([m for m in mixing if "TUMBLER" in m["pattern_type"]]),
        "fan_out_dispersion_count": len([m for m in mixing if "FAN_OUT" in m["pattern_type"]]),
    }
