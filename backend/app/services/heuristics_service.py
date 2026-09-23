"""
BTC-SHIELD Structural Heuristics Service
Detects peeling chains, CoinJoin/mixing patterns, and high fan-in/fan-out topologies.
Memory-Optimized: Bounded processing with zero full-dataset scans.
Supports both relational (Dataset 6) and legacy input/output database schemas.
"""
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from app.models.models import Transaction, TransactionInput, TransactionOutput, Wallet, RawRecord
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


class TxWrapper:
    """Lightweight abstraction for transactions across both relational and legacy schemas."""
    def __init__(self, id_val, txid, timestamp=None, fee=0.0, total_input=0.0, total_output=0.0):
        self.id = id_val
        self.txid = txid
        self.timestamp = timestamp
        self.fee = float(fee or 0.0)
        self.total_input = float(total_input or 0.0)
        self.total_output = float(total_output or 0.0)


class IOWrapper:
    """Lightweight abstraction for input/output records."""
    def __init__(self, wallet_address, amount, position=0):
        self.wallet_address = wallet_address
        self.amount = float(amount or 0.0)
        self.position = position


def get_tx_io_map(db: Session, limit: int = 2000):
    """
    Extracts bounded transactions with inputs and outputs.
    Automatically switches between TransactionInput/Output tables and RawRecord audit logs.
    """
    txs = db.query(Transaction).order_by(Transaction.timestamp.desc().nullslast()).limit(limit).all()
    if not txs:
        # Check if raw records exist
        raws = db.query(RawRecord).limit(limit).all()
        if not raws:
            return [], {}, {}, {}

        tx_list = []
        inputs_by_tx = defaultdict(list)
        outputs_by_tx = defaultdict(list)
        tx_by_txid = {}

        for r in raws:
            data = r.raw_data
            if not isinstance(data, dict):
                continue
            txid = data.get("txid")
            if not txid:
                continue

            ts_raw = data.get("timestamp")
            ts = None
            if ts_raw:
                try:
                    ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
                except Exception:
                    pass

            in_addrs = [a for a in str(data.get("input_addresses", "")).split(";") if a]
            out_addrs = [a for a in str(data.get("output_addresses", "")).split(";") if a]
            in_amts = [float(x) for x in str(data.get("input_amounts", "")).split(";") if x]
            out_amts = [float(x) for x in str(data.get("output_amounts", "")).split(";") if x]

            tx_obj = TxWrapper(
                id_val=r.id,
                txid=txid,
                timestamp=ts,
                fee=float(data.get("fee") or 0.0),
                total_input=sum(in_amts),
                total_output=sum(out_amts)
            )
            tx_list.append(tx_obj)
            tx_by_txid[txid] = tx_obj

            for idx, (addr, amt) in enumerate(zip(in_addrs, in_amts)):
                inputs_by_tx[tx_obj.id].append(IOWrapper(addr, amt, idx))
            for idx, (addr, amt) in enumerate(zip(out_addrs, out_amts)):
                outputs_by_tx[tx_obj.id].append(IOWrapper(addr, amt, idx))

        return tx_list, inputs_by_tx, outputs_by_tx, tx_by_txid

    tx_ids = [t.id for t in txs]
    tx_by_id = {t.id: t for t in txs}
    tx_by_txid = {t.txid: t for t in txs}

    inputs_by_tx = defaultdict(list)
    outputs_by_tx = defaultdict(list)

    # Check if TransactionInput is populated
    has_inputs = db.query(TransactionInput.id).filter(TransactionInput.transaction_id.in_(tx_ids)).first() is not None

    if has_inputs:
        for inp in db.query(TransactionInput).filter(TransactionInput.transaction_id.in_(tx_ids)).all():
            inputs_by_tx[inp.transaction_id].append(IOWrapper(inp.wallet_address, inp.amount, inp.position))
        for out in db.query(TransactionOutput).filter(TransactionOutput.transaction_id.in_(tx_ids)).all():
            outputs_by_tx[out.transaction_id].append(IOWrapper(out.wallet_address, out.amount, out.position))
    else:
        # Fallback to RawRecord for relational 100k schema
        raws = db.query(RawRecord).limit(limit).all()
        for r in raws:
            data = r.raw_data
            if not isinstance(data, dict):
                continue
            txid = data.get("txid")
            tx_obj = tx_by_txid.get(txid)
            if not tx_obj:
                continue

            in_addrs = [a for a in str(data.get("input_addresses", "")).split(";") if a]
            out_addrs = [a for a in str(data.get("output_addresses", "")).split(";") if a]
            in_amts = [float(x) for x in str(data.get("input_amounts", "")).split(";") if x]
            out_amts = [float(x) for x in str(data.get("output_amounts", "")).split(";") if x]

            for idx, (addr, amt) in enumerate(zip(in_addrs, in_amts)):
                inputs_by_tx[tx_obj.id].append(IOWrapper(addr, amt, idx))
            for idx, (addr, amt) in enumerate(zip(out_addrs, out_amts)):
                outputs_by_tx[tx_obj.id].append(IOWrapper(addr, amt, idx))

    return txs, inputs_by_tx, outputs_by_tx, tx_by_txid


def detect_peeling_chains(db: Session, min_hops: int = 2, limit: int = 50) -> list[dict]:
    """
    Detect peeling chains across transactions.
    Identifies multi-hop change-peeling cascades and high-asymmetry peeling structures.
    """
    txs, inputs_by_tx, outputs_by_tx, tx_by_txid = get_tx_io_map(db, limit=2000)
    if not txs:
        return []

    tx_by_id = {tx.id: tx for tx in txs}
    candidate_txids = set()
    spending_map = defaultdict(list)
    single_peel_candidates = []

    for tx in txs:
        inps = inputs_by_tx.get(tx.id, [])
        outs = outputs_by_tx.get(tx.id, [])

        for inp in inps:
            if inp.wallet_address:
                spending_map[inp.wallet_address].append(tx)

        if len(outs) == 2 and 1 <= len(inps) <= 2:
            candidate_txids.add(tx.txid)
            o1, o2 = outs[0], outs[1]
            peel_out = o1 if o1.amount <= o2.amount else o2
            change_out = o2 if o1.amount <= o2.amount else o1
            asym = peel_out.amount / max(change_out.amount, 0.000001)
            if asym < 0.35:
                single_peel_candidates.append((tx, peel_out, change_out, asym))
        elif len(outs) >= 3 and len(inps) == 1:
            # Fan-out peeling
            candidate_txids.add(tx.txid)

    visited_txids = set()
    chains = []

    sorted_candidates = sorted(
        [tx_by_txid[t] for t in candidate_txids if t in tx_by_txid and getattr(tx_by_txid[t], "timestamp", None)],
        key=lambda x: x.timestamp or datetime.min
    )
    if not sorted_candidates:
        sorted_candidates = [tx_by_txid[t] for t in candidate_txids if t in tx_by_txid]

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
            if len(outs) < 2:
                break

            if len(outs) == 2:
                out1, out2 = outs[0], outs[1]
                peel_out = out1 if out1.amount <= out2.amount else out2
                change_out = out2 if out1.amount <= out2.amount else out1
            else:
                # In multi-output fan-out peel: smaller outputs are peeled, largest is change
                sorted_outs = sorted(outs, key=lambda o: o.amount)
                change_out = sorted_outs[-1]
                peel_out = sorted_outs[0]

            total_peeled += peel_out.amount
            if peel_out.wallet_address:
                chain_addresses.add(peel_out.wallet_address)
            if change_out.wallet_address:
                chain_addresses.add(change_out.wallet_address)

            current_chain_hops.append({
                "hop": len(current_chain_hops) + 1,
                "txid": current_tx.txid,
                "timestamp": current_tx.timestamp.isoformat() if getattr(current_tx, "timestamp", None) else None,
                "peeled_amount": round(peel_out.amount, 6),
                "peeled_address": peel_out.wallet_address,
                "change_amount": round(change_out.amount, 6),
                "change_address": change_out.wallet_address,
                "fee": getattr(current_tx, "fee", 0.0) or 0.0,
            })

            # Check if change_out was subsequently spent
            next_tx = None
            if change_out.wallet_address and change_out.wallet_address in spending_map:
                possible_spends = [
                    sp for sp in spending_map[change_out.wallet_address]
                    if sp.txid != current_tx.txid
                    and sp.txid in candidate_txids
                ]
                if possible_spends:
                    possible_spends.sort(key=lambda x: x.timestamp if getattr(x, "timestamp", None) else datetime.min)
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
                "confidence_score": min(98.0, 50.0 + (len(current_chain_hops) * 12.0)),
                "hops": current_chain_hops
            })
            if len(chains) >= limit:
                break

    # If few multi-hop chains found and min_hops <= 1, supplement with high-confidence single peeling steps
    if len(chains) < limit and min_hops <= 1:
        for tx, peel_out, change_out, asym in single_peel_candidates:
            if tx.txid in visited_txids:
                continue
            chains.append({
                "chain_id": f"peel_{tx.txid[:10]}",
                "start_txid": tx.txid,
                "terminal_txid": tx.txid,
                "hop_count": 1,
                "total_peeled_btc": round(peel_out.amount, 6),
                "initial_amount_btc": round(peel_out.amount + change_out.amount, 6),
                "final_change_btc": round(change_out.amount, 6),
                "unique_addresses_count": 2,
                "confidence_score": round(max(60.0, 85.0 - (asym * 50.0)), 1),
                "hops": [{
                    "hop": 1,
                    "txid": tx.txid,
                    "timestamp": tx.timestamp.isoformat() if getattr(tx, "timestamp", None) else None,
                    "peeled_amount": round(peel_out.amount, 6),
                    "peeled_address": peel_out.wallet_address,
                    "change_amount": round(change_out.amount, 6),
                    "change_address": change_out.wallet_address,
                    "fee": getattr(tx, "fee", 0.0) or 0.0,
                }]
            })
            if len(chains) >= limit:
                break

    chains.sort(key=lambda c: (c["hop_count"], c["confidence_score"], c["total_peeled_btc"]), reverse=True)
    return chains[:limit]


def detect_mixing_patterns(db: Session, limit: int = 50) -> list[dict]:
    """
    Detect CoinJoin and mixing/tumbling patterns.
    Indicators:
    1. Equal output values (standard CoinJoin fingerprint).
    2. High input count + high output count (many-to-many topology).
    3. Output entropy profile (uniform distribution across participants).
    """
    txs, inputs_by_tx, outputs_by_tx, _ = get_tx_io_map(db, limit=2000)
    if not txs:
        return []

    mix_records = []

    for tx in txs:
        outs = outputs_by_tx.get(tx.id, [])
        inps = inputs_by_tx.get(tx.id, [])

        if len(outs) < 2:
            continue

        amount_groups = defaultdict(list)
        out_amounts = []
        for o in outs:
            amt_rounded = round(o.amount, 4)
            amount_groups[amt_rounded].append(o.wallet_address)
            out_amounts.append(o.amount)

        equal_clusters = {amt: addrs for amt, addrs in amount_groups.items() if len(addrs) >= 2}
        max_equal_count = max([len(addrs) for addrs in amount_groups.values()], default=0)

        entropy = compute_entropy(out_amounts)
        input_count = len(inps)
        output_count = len(outs)

        is_coinjoin = False
        is_tumbler = False
        mix_type = "STANDARD"
        confidence = 0.0

        # Heuristic 1: CoinJoin Equal Denomination
        if max_equal_count >= 3:
            is_coinjoin = True
            mix_type = "EQUAL_DENOMINATION_COINJOIN"
            confidence = min(98.0, 60.0 + (max_equal_count * 5.0))
        elif max_equal_count == 2 and input_count >= 2:
            is_coinjoin = True
            mix_type = "PARTIAL_DENOMINATION_COINJOIN"
            confidence = 65.0
        # Heuristic 2: Many-to-Many Multi-Party Tumbler
        elif input_count >= 3 and output_count >= 3:
            is_tumbler = True
            mix_type = "MANY_TO_MANY_TUMBLER"
            confidence = min(92.0, 50.0 + ((input_count + output_count) * 2.5))
        # Heuristic 3: High Fan-Out Dispersion (1 to 5+)
        elif input_count == 1 and output_count >= 5:
            mix_type = "HIGH_FAN_OUT_DISPERSION"
            confidence = min(88.0, 45.0 + (output_count * 3.5))

        if is_coinjoin or is_tumbler or mix_type != "STANDARD":
            mix_records.append({
                "txid": tx.txid,
                "timestamp": tx.timestamp.isoformat() if getattr(tx, "timestamp", None) else None,
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
                "total_volume_btc": round(getattr(tx, "total_output", 0.0) or 0.0, 6),
                "fee_btc": round(getattr(tx, "fee", 0.0) or 0.0, 6)
            })

    mix_records.sort(key=lambda m: (m["confidence_score"], m["output_count"]), reverse=True)
    return mix_records[:limit]


def analyze_transaction_heuristics(db: Session, txid: str) -> dict:
    """Analyze single transaction for peeling, mixing, and fan-out/fan-in structures."""
    tx = db.query(Transaction).filter(Transaction.txid == txid).first()
    in_addrs = []
    out_addrs = []
    amounts = []
    timestamp = None
    fee = 0.0
    total_output = 0.0

    if tx:
        timestamp = tx.timestamp.isoformat() if tx.timestamp else None
        fee = tx.fee or 0.0
        total_output = tx.total_output or 0.0

        inps = db.query(TransactionInput).filter(TransactionInput.transaction_id == tx.id).all()
        outs = db.query(TransactionOutput).filter(TransactionOutput.transaction_id == tx.id).all()
        if inps or outs:
            in_addrs = [i.wallet_address for i in inps if i.wallet_address]
            out_addrs = [o.wallet_address for o in outs if o.wallet_address]
            amounts = [o.amount for o in outs]

    # Fallback to RawRecord
    if not amounts:
        raw = db.query(RawRecord).filter(
            cast(RawRecord.raw_data, String).like(f'%{txid}%')
        ).first()
        if raw and isinstance(raw.raw_data, dict):
            timestamp = str(raw.raw_data.get("timestamp", ""))
            fee = float(raw.raw_data.get("fee") or 0.0)
            in_addrs = [a for a in str(raw.raw_data.get("input_addresses", "")).split(";") if a]
            out_addrs = [a for a in str(raw.raw_data.get("output_addresses", "")).split(";") if a]
            amounts = [float(x) for x in str(raw.raw_data.get("output_amounts", "")).split(";") if x]
            total_output = sum(amounts)

    if not amounts and not in_addrs:
        return {"found": False, "message": "Transaction not found in database or audit logs"}

    in_count = len(in_addrs)
    out_count = len(out_addrs)
    entropy = compute_entropy(amounts)

    amt_counts = defaultdict(int)
    for a in amounts:
        amt_counts[round(a, 4)] += 1
    max_equal = max(amt_counts.values(), default=0)

    is_peeling_candidate = False
    asymmetry_ratio = 0.0
    if out_count == 2 and 1 <= in_count <= 2 and amounts:
        is_peeling_candidate = True
        min_a = min(amounts)
        max_a = max(amounts) if max(amounts) > 0 else 1.0
        asymmetry_ratio = min_a / max_a

    detected_patterns = []
    if max_equal >= 3:
        detected_patterns.append("COINJOIN_EQUAL_OUTPUTS")
    if in_count >= 3 and out_count >= 3:
        detected_patterns.append("MANY_TO_MANY_TUMBLER")
    if in_count == 1 and out_count >= 5:
        detected_patterns.append("FAN_OUT_DISPERSION")
    if in_count >= 5 and out_count == 1:
        detected_patterns.append("FAN_IN_CONSOLIDATION")
    if is_peeling_candidate and asymmetry_ratio < 0.35:
        detected_patterns.append("PEELING_CHAIN_STEP")

    return {
        "found": True,
        "txid": txid,
        "timestamp": timestamp,
        "input_count": in_count,
        "output_count": out_count,
        "total_volume_btc": round(total_output, 6),
        "fee_btc": round(fee, 6),
        "entropy_bits": round(entropy, 3),
        "max_equal_outputs": max_equal,
        "is_peeling_candidate": is_peeling_candidate,
        "asymmetry_ratio": round(asymmetry_ratio, 3),
        "detected_patterns": detected_patterns or ["STANDARD_TRANSFER"],
        "structural_risk_level": "HIGH" if any(p in ["COINJOIN_EQUAL_OUTPUTS", "MANY_TO_MANY_TUMBLER", "PEELING_CHAIN_STEP"] for p in detected_patterns) else "LOW"
    }


def get_heuristics_summary(db: Session) -> dict:
    """Get high-level summary of structural patterns across the database."""
    # Allow min_hops=1 to capture structuring transactions if multi-hop is limited
    peeling = detect_peeling_chains(db, min_hops=1, limit=100)
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
