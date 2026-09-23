from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, cast, String
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.models import User, Transaction, TransactionInput, TransactionOutput, RawRecord, GraphEdge
from app.schemas.schemas import TransactionResponse, TransactionDetailResponse
from typing import List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[TransactionResponse])
def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List transactions with strict bounded pagination and indexed ordering."""
    query = db.query(Transaction)
    if search and len(search.strip()) >= 3:
        clean_search = search.strip()
        for p in ["TX:", "tx:", "TRANSACTION:", "transaction:"]:
            if clean_search.startswith(p):
                clean_search = clean_search[len(p):].strip()
        query = query.filter(
            or_(
                Transaction.txid.ilike(f"{clean_search}%"),
                Transaction.txid.ilike(f"TX:{clean_search}%")
            )
        )

    return query.order_by(
        Transaction.timestamp.desc().nullslast(),
        Transaction.id.desc()
    ).offset(skip).limit(limit).all()

@router.get("/{txid}", response_model=TransactionDetailResponse)
def get_transaction(txid: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Get single transaction with bounded inputs/outputs, supporting relational graph and audit fallbacks."""
    clean_txid = (txid or "").strip()
    for prefix in ["TRANSACTION:", "transaction:", "TX:", "tx:"]:
        if clean_txid.startswith(prefix):
            clean_txid = clean_txid[len(prefix):].strip()

    # 1. Primary lookup in Transaction table
    tx = db.query(Transaction).filter(
        or_(
            Transaction.txid == clean_txid,
            Transaction.txid == f"TX:{clean_txid}",
            Transaction.txid == txid
        )
    ).first()

    if tx:
        inps = db.query(TransactionInput).filter(TransactionInput.transaction_id == tx.id).order_by(TransactionInput.position.asc()).limit(100).all()
        outs = db.query(TransactionOutput).filter(TransactionOutput.transaction_id == tx.id).order_by(TransactionOutput.position.asc()).limit(100).all()

        inputs_list = [
            {
                "wallet_address": inp.wallet_address or "",
                "amount": inp.amount or 0.0,
                "position": inp.position or 0
            }
            for inp in inps if inp.wallet_address
        ]
        outputs_list = [
            {
                "wallet_address": out.wallet_address or "",
                "amount": out.amount or 0.0,
                "position": out.position or 0
            }
            for out in outs if out.wallet_address
        ]

        # If inputs/outputs are missing in relational tables, enrich from RawRecord
        if not inputs_list and not outputs_list:
            raw = db.query(RawRecord).filter(
                cast(RawRecord.raw_data, String).like(f'%{clean_txid}%')
            ).first()
            if raw and isinstance(raw.raw_data, dict):
                in_addrs = [a for a in str(raw.raw_data.get("input_addresses", "")).split(";") if a]
                in_amts = [float(x) for x in str(raw.raw_data.get("input_amounts", "")).split(";") if x]
                out_addrs = [a for a in str(raw.raw_data.get("output_addresses", "")).split(";") if a]
                out_amts = [float(x) for x in str(raw.raw_data.get("output_amounts", "")).split(";") if x]
                for idx, addr in enumerate(in_addrs):
                    inputs_list.append({
                        "wallet_address": addr,
                        "amount": in_amts[idx] if idx < len(in_amts) else 0.0,
                        "position": idx
                    })
                for idx, addr in enumerate(out_addrs):
                    outputs_list.append({
                        "wallet_address": addr,
                        "amount": out_amts[idx] if idx < len(out_amts) else 0.0,
                        "position": idx
                    })

        tot_in = tx.total_input or (sum(i["amount"] for i in inputs_list) if inputs_list else 0.0)
        tot_out = tx.total_output or (sum(o["amount"] for o in outputs_list) if outputs_list else 0.0)

        return TransactionDetailResponse(
            id=tx.id,
            txid=tx.txid,
            timestamp=tx.timestamp,
            fee=tx.fee or 0.0,
            script_type=tx.script_type or "p2pkh",
            total_input=tot_in,
            total_output=tot_out,
            inputs=inputs_list,
            outputs=outputs_list
        )

    # 2. Secondary lookup in RawRecord (audit logs / CSV records)
    raw = db.query(RawRecord).filter(
        cast(RawRecord.raw_data, String).like(f'%{clean_txid}%')
    ).first()

    if raw and isinstance(raw.raw_data, dict):
        raw_d = raw.raw_data
        ts_val = raw_d.get("timestamp")
        parsed_ts = None
        if ts_val:
            try:
                parsed_ts = datetime.fromisoformat(str(ts_val).replace("Z", "+00:00"))
            except Exception:
                parsed_ts = getattr(raw, "created_at", None)

        fee = float(raw_d.get("fee") or 0.0)
        script_type = str(raw_d.get("script_type") or "p2pkh")
        in_addrs = [a for a in str(raw_d.get("input_addresses", "")).split(";") if a]
        in_amts = [float(x) for x in str(raw_d.get("input_amounts", "")).split(";") if x]
        out_addrs = [a for a in str(raw_d.get("output_addresses", "")).split(";") if a]
        out_amts = [float(x) for x in str(raw_d.get("output_amounts", "")).split(";") if x]

        inputs_list = [
            {
                "wallet_address": addr,
                "amount": in_amts[idx] if idx < len(in_amts) else 0.0,
                "position": idx
            }
            for idx, addr in enumerate(in_addrs)
        ]
        outputs_list = [
            {
                "wallet_address": addr,
                "amount": out_amts[idx] if idx < len(out_amts) else 0.0,
                "position": idx
            }
            for idx, addr in enumerate(out_addrs)
        ]
        tot_in = sum(i["amount"] for i in inputs_list) if inputs_list else float(raw_d.get("total_input") or 0.0)
        tot_out = sum(o["amount"] for o in outputs_list) if outputs_list else float(raw_d.get("total_output") or 0.0)

        return TransactionDetailResponse(
            id=raw.id or 0,
            txid=str(raw_d.get("txid") or clean_txid),
            timestamp=parsed_ts,
            fee=fee,
            script_type=script_type,
            total_input=tot_in,
            total_output=tot_out,
            inputs=inputs_list,
            outputs=outputs_list
        )

    # 3. Tertiary lookup in GraphEdge (relational graph bundle)
    edges = db.query(GraphEdge).filter(
        or_(
            GraphEdge.source_id == clean_txid,
            GraphEdge.source_id == f"TX:{clean_txid}",
            GraphEdge.target_id == clean_txid,
            GraphEdge.target_id == f"TX:{clean_txid}",
            cast(GraphEdge.properties, String).like(f'%{clean_txid}%')
        )
    ).limit(50).all()

    if edges:
        inputs_list = []
        outputs_list = []
        tot_in = 0.0
        tot_out = 0.0

        for idx, ge in enumerate(edges):
            w_addr = None
            if isinstance(ge.properties, dict) and ge.properties.get("wallet_address"):
                w_addr = ge.properties["wallet_address"]
            elif ge.source_type == "WALLET":
                w_addr = ge.source_id.replace("WALLET:", "")
            elif ge.target_type == "WALLET":
                w_addr = ge.target_id.replace("WALLET:", "")

            amt = float(ge.weight or 0.0)
            if ge.edge_type == "INPUT_OF" or ge.target_id in [clean_txid, f"TX:{clean_txid}"]:
                if w_addr:
                    inputs_list.append({"wallet_address": w_addr, "amount": amt, "position": len(inputs_list)})
                    tot_in += amt
            elif ge.edge_type == "OUTPUT_OF" or ge.source_id in [clean_txid, f"TX:{clean_txid}"]:
                if w_addr:
                    outputs_list.append({"wallet_address": w_addr, "amount": amt, "position": len(outputs_list)})
                    tot_out += amt

        return TransactionDetailResponse(
            id=0,
            txid=clean_txid,
            timestamp=edges[0].created_at if hasattr(edges[0], "created_at") else None,
            fee=0.0,
            script_type="p2pkh",
            total_input=tot_in,
            total_output=tot_out,
            inputs=inputs_list,
            outputs=outputs_list
        )

    raise HTTPException(status_code=404, detail=f"Transaction '{clean_txid}' not found")
