"""
BTC-SHIELD Ingestion Service
Multi-format data ingestion with validation, normalization, and quality tracking.
"""
import json
import csv
import io
import ast
try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
from sqlalchemy.orm import Session
from app.models.models import (
    Dataset, RawRecord, Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, Wallet, IPEntity, ASNEntity
)
from datetime import datetime
from typing import Optional, Union, List, Dict, Any
import re
import logging
import hashlib

logger = logging.getLogger(__name__)

import ipaddress

def validate_ip(ip: str) -> bool:
    """Validate IPv4 or IPv6 address format."""
    if not ip or not isinstance(ip, str):
        return False
    try:
        ipaddress.ip_address(ip.strip())
        return True
    except ValueError:
        return False

def validate_bitcoin_address(addr: str) -> bool:
    """Basic Bitcoin address format validation."""
    if not addr or len(addr) < 10:
        return False
    # P2PKH: starts with 1, P2SH: starts with 3, Bech32: starts with bc1
    if addr.startswith("1") or addr.startswith("3"):
        return len(addr) >= 25 and len(addr) <= 34
    if addr.startswith("bc1"):
        return len(addr) >= 14 and len(addr) <= 74
    return True  # Allow other formats for flexibility

def validate_txid(txid: str) -> bool:
    """Validate 64-character hexadecimal Bitcoin transaction ID."""
    if not txid or not isinstance(txid, str):
        return False
    clean = txid.strip()
    if len(clean) != 64:
        return False
    return bool(re.fullmatch(r"^[0-9a-fA-F]{64}$", clean))

def normalize_timestamp(ts) -> Optional[datetime]:
    """Normalize various timestamp formats to datetime."""
    if not ts:
        return None
    if isinstance(ts, datetime):
        return ts
    ts_str = str(ts).strip()
    # Try ISO 8601 variants
    for fmt in [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S+00:00",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]:
        try:
            return datetime.strptime(ts_str, fmt)
        except ValueError:
            continue
    # Try fromisoformat as fallback
    try:
        return datetime.fromisoformat(ts_str.replace("Z", "+00:00").replace("+00:00", ""))
    except Exception:
        return None

def safe_float(val, default=0.0) -> float:
    """Safely convert to float."""
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def parse_address_list(raw_val) -> list[str]:
    """
    Polyglot address list parser supporting:
    A. Native Python list/tuple: ["addr1", "addr2"]
    B. JSON-stringified arrays: '["addr1", "addr2"]'
    C. Legacy semicolon-separated strings: "addr1;addr2" or comma-separated
    """
    if not raw_val:
        return []
    if isinstance(raw_val, (list, tuple)):
        return [str(a).strip() for a in raw_val if str(a).strip()]
    if isinstance(raw_val, str):
        val_str = raw_val.strip()
        if not val_str:
            return []
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, (list, tuple)):
                    return [str(a).strip() for a in parsed if str(a).strip()]
            except (json.JSONDecodeError, ValueError):
                try:
                    parsed = ast.literal_eval(val_str)
                    if isinstance(parsed, (list, tuple)):
                        return [str(a).strip() for a in parsed if str(a).strip()]
                except Exception:
                    val_str = val_str[1:-1]
        if ";" in val_str:
            parts = val_str.split(";")
        elif "," in val_str:
            parts = val_str.split(",")
        else:
            parts = [val_str]
        return [p.strip().strip("'\"").strip() for p in parts if p.strip().strip("'\"").strip()]
    return [str(raw_val).strip()]

def parse_amount_list(raw_val) -> list[float]:
    """
    Polyglot amount list parser supporting:
    A. Native Python list/tuple: [0.5, 1.2] or ["0.5", "1.2"]
    B. JSON-stringified arrays: '[0.5, 1.2]' or '["0.5", "1.2"]'
    C. Semicolon-separated or comma-separated strings: "0.5;1.2"
    """
    if raw_val is None or raw_val == "":
        return []
    if isinstance(raw_val, (int, float)):
        return [float(raw_val)]
    if isinstance(raw_val, (list, tuple)):
        res = []
        for a in raw_val:
            try:
                res.append(float(a))
            except (ValueError, TypeError):
                res.append(0.0)
        return res
    if isinstance(raw_val, str):
        val_str = raw_val.strip()
        if not val_str:
            return []
        if val_str.startswith("[") and val_str.endswith("]"):
            try:
                parsed = json.loads(val_str)
                if isinstance(parsed, (list, tuple)):
                    return parse_amount_list(parsed)
            except (json.JSONDecodeError, ValueError):
                try:
                    parsed = ast.literal_eval(val_str)
                    if isinstance(parsed, (list, tuple)):
                        return parse_amount_list(parsed)
                except Exception:
                    val_str = val_str[1:-1]
        if ";" in val_str:
            parts = val_str.split(";")
        elif "," in val_str:
            parts = val_str.split(",")
        else:
            parts = [val_str]
        res = []
        for p in parts:
            item = p.strip().strip("'\"").strip()
            if item:
                try:
                    res.append(float(item))
                except (ValueError, TypeError):
                    res.append(0.0)
        return res
    try:
        return [float(raw_val)]
    except (ValueError, TypeError):
        return []

def calculate_fee(raw_fee, total_input: float, total_output: float) -> float:
    """
    Fee calculation:
    - If explicit fee is present, preserve/use it.
    - If fee is absent (None or empty string): fee = max(0.0, round(total_input - total_output, 8))
    """
    if raw_fee is not None and str(raw_fee).strip() != "":
        try:
            return float(raw_fee)
        except (ValueError, TypeError):
            pass
    return max(0.0, round(total_input - total_output, 8))

def detect_format(filename: str) -> str:
    """Detect file format from extension."""
    fname = filename.lower()
    if fname.endswith(".json"):
        return "json"
    if fname.endswith(".csv"):
        return "csv"
    if fname.endswith(".xml"):
        return "xml"
    return "unknown"


# --- Parsers ---

def parse_csv_content(content_str: str) -> list[dict]:
    """Parse CSV content into list of dicts."""
    reader = csv.DictReader(io.StringIO(content_str))
    return list(reader)

def parse_json_content(content_str: str) -> list[dict]:
    """Parse JSON content into list of dicts."""
    data = json.loads(content_str)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        # Check for common wrapper patterns
        if "transactions" in data:
            return data["transactions"]
        if "records" in data:
            return data["records"]
        if "data" in data:
            return data["data"]
        return [data]
    return []

def parse_xml_content(content_str: str) -> list[dict]:
    """Parse XML content into list of dicts."""
    records = []
    try:
        root = ET.fromstring(content_str)
        for elem in root:
            record = {}
            for child in elem:
                record[child.tag] = child.text
            if record:
                records.append(record)
    except ET.ParseError as e:
        logger.error(f"XML parse error: {e}")
    return records


# --- Record Validation ---

def validate_record(rec: dict) -> tuple[bool, str]:
    """
    Validate a single record. Returns (is_valid, error_message).
    Required: txid, timestamp. Everything else is optional but validated if present.
    """
    errors = []

    if not rec.get("txid"):
        errors.append("missing txid")

    if not rec.get("timestamp"):
        errors.append("missing timestamp")
    elif normalize_timestamp(rec["timestamp"]) is None:
        errors.append(f"invalid timestamp format: {rec['timestamp']}")

    # Validate IPs if present
    if rec.get("src_ip") and not validate_ip(rec["src_ip"]):
        errors.append(f"invalid src_ip: {rec['src_ip']}")
    if rec.get("dst_ip") and not validate_ip(rec["dst_ip"]):
        errors.append(f"invalid dst_ip: {rec['dst_ip']}")

    # Validate amounts
    if rec.get("fee"):
        try:
            float(rec["fee"])
        except (ValueError, TypeError):
            errors.append(f"invalid fee: {rec['fee']}")

    if errors:
        return False, "; ".join(errors)
    return True, ""


# --- Duplicate Detection ---

def compute_record_hash(rec: dict) -> str:
    """Compute a hash for duplicate detection."""
    key_fields = f"{rec.get('txid', '')}-{rec.get('timestamp', '')}-{rec.get('src_ip', '')}"
    return hashlib.md5(key_fields.encode()).hexdigest()


# --- Main Processing ---

def process_dataset(db: Session, dataset_id: int, file_content: bytes):
    """
    Full ingestion pipeline:
    1. Parse file content based on format
    2. Validate each record
    3. Detect duplicates
    4. Store raw records (immutable)
    5. Create normalized entities (transactions, wallets, IPs, network observations)
    6. Track data quality metrics
    """
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise ValueError(f"Dataset {dataset_id} not found")

    dataset.status = "PROCESSING"
    db.commit()

    try:
        content_str = file_content.decode("utf-8")

        # Parse based on format
        if dataset.format == "json":
            records = parse_json_content(content_str)
        elif dataset.format == "csv":
            records = parse_csv_content(content_str)
        elif dataset.format == "xml":
            records = parse_xml_content(content_str)
        else:
            dataset.status = "FAILED"
            db.commit()
            raise ValueError(f"Unsupported format: {dataset.format}")

        total = len(records)
        valid_count = 0
        invalid_count = 0
        duplicate_count = 0
        seen_hashes = set()

        dataset.total_records = total

        # Pre-populate existing TXIDs and entity caches to avoid per-record DB round-trips
        existing_txids = set(r[0] for r in db.query(Transaction.txid).all())
        wallet_cache = {}
        ip_cache = {}
        asn_cache = {}

        orig_expire = getattr(db, "expire_on_commit", True)
        db.expire_on_commit = False

        for i, rec in enumerate(records):
            try:
                # Validate
                is_valid, error_msg = validate_record(rec)

                # Duplicate detection
                rec_hash = compute_record_hash(rec)
                is_duplicate = rec_hash in seen_hashes
                if is_duplicate:
                    duplicate_count += 1
                    error_msg = (error_msg + "; " if error_msg else "") + "duplicate record"
                    is_valid = False
                seen_hashes.add(rec_hash)

                # Store raw record (immutable)
                raw = RawRecord(
                    dataset_id=dataset.id,
                    line_number=i + 1,
                    raw_data=rec,
                    is_valid=is_valid,
                    error_message=error_msg if not is_valid else None
                )
                db.add(raw)

                if not is_valid:
                    invalid_count += 1
                    continue

                # --- Create normalized entities ---
                ts = normalize_timestamp(rec.get("timestamp"))

                # Polyglot address and amount parsing
                input_addrs = parse_address_list(rec.get("input_addresses"))
                output_addrs = parse_address_list(rec.get("output_addresses"))
                input_amts = parse_amount_list(rec.get("input_amounts"))
                output_amts = parse_amount_list(rec.get("output_amounts"))

                total_input = round(sum(input_amts), 8) if input_amts else 0.0
                total_output = round(sum(output_amts), 8) if output_amts else 0.0
                fee = calculate_fee(rec.get("fee"), total_input, total_output)

                # Create or get transaction
                txid = rec["txid"]
                if txid in existing_txids:
                    pass
                else:
                    existing_txids.add(txid)
                    tx = Transaction(
                        dataset_id=dataset.id,
                        txid=txid,
                        timestamp=ts,
                        fee=fee,
                        script_type=rec.get("script_type", ""),
                        total_input=total_input,
                        total_output=total_output,
                    )
                    db.add(tx)
                    db.flush()

                    # Create transaction inputs
                    for pos, addr in enumerate(input_addrs):
                        amt = input_amts[pos] if pos < len(input_amts) else 0.0
                        ti = TransactionInput(
                            transaction_id=tx.id,
                            wallet_address=addr,
                            amount=amt,
                            position=pos
                        )
                        db.add(ti)

                    # Create transaction outputs
                    for pos, addr in enumerate(output_addrs):
                        amt = output_amts[pos] if pos < len(output_amts) else 0.0
                        to = TransactionOutput(
                            transaction_id=tx.id,
                            wallet_address=addr,
                            amount=amt,
                            position=pos
                        )
                        db.add(to)

                    # Resolve wallet entities
                    all_addrs = set(input_addrs + output_addrs)
                    for addr in all_addrs:
                        wallet = wallet_cache.get(addr)
                        if not wallet:
                            wallet = db.query(Wallet).filter(Wallet.address == addr).first()
                            if not wallet:
                                wallet = Wallet(
                                    address=addr,
                                    first_seen=ts,
                                    last_seen=ts,
                                    total_sent=0.0,
                                    total_received=0.0,
                                    tx_count=0
                                )
                                db.add(wallet)
                            wallet_cache[addr] = wallet

                        # Update wallet stats
                        wallet.tx_count = (wallet.tx_count or 0) + 1
                        if ts and (wallet.last_seen is None or ts > wallet.last_seen):
                            wallet.last_seen = ts
                        if ts and (wallet.first_seen is None or ts < wallet.first_seen):
                            wallet.first_seen = ts

                        if addr in input_addrs:
                            idx = input_addrs.index(addr)
                            amt = input_amts[idx] if idx < len(input_amts) else 0.0
                            wallet.total_sent = (wallet.total_sent or 0.0) + amt
                        if addr in output_addrs:
                            idx = output_addrs.index(addr)
                            amt = output_amts[idx] if idx < len(output_amts) else 0.0
                            wallet.total_received = (wallet.total_received or 0.0) + amt

                # Create network observation
                if rec.get("src_ip"):
                    src_ip = rec["src_ip"]
                    net_obs = NetworkObservation(
                        dataset_id=dataset.id,
                        transaction_id=txid,
                        src_ip=src_ip,
                        dst_ip=rec.get("dst_ip", ""),
                        src_port=int(rec.get("src_port", 0)) if rec.get("src_port") else None,
                        dst_port=int(rec.get("dst_port", 0)) if rec.get("dst_port") else None,
                        timestamp=ts,
                        geo_country=rec.get("geo_country", ""),
                        asn=rec.get("asn", "")
                    )
                    db.add(net_obs)

                    # Resolve IP entity
                    ip_ent = ip_cache.get(src_ip)
                    if not ip_ent:
                        ip_ent = db.query(IPEntity).filter(IPEntity.ip_address == src_ip).first()
                        if not ip_ent:
                            ip_ent = IPEntity(
                                ip_address=src_ip,
                                first_seen=ts,
                                last_seen=ts,
                                observation_count=0,
                                asn=rec.get("asn", ""),
                                country=rec.get("geo_country", "")
                            )
                            db.add(ip_ent)
                        ip_cache[src_ip] = ip_ent
                    ip_ent.observation_count = (ip_ent.observation_count or 0) + 1
                    if ts and (ip_ent.last_seen is None or ts > ip_ent.last_seen):
                        ip_ent.last_seen = ts

                    # Resolve ASN entity
                    asn_val = rec.get("asn", "")
                    if asn_val:
                        asn_ent = asn_cache.get(asn_val)
                        if not asn_ent:
                            asn_ent = db.query(ASNEntity).filter(ASNEntity.asn_number == asn_val).first()
                            if not asn_ent:
                                asn_ent = ASNEntity(
                                    asn_number=asn_val,
                                    name=f"ASN {asn_val}",
                                    country_count=0,
                                    ip_count=0
                                )
                                db.add(asn_ent)
                            asn_cache[asn_val] = asn_ent

                valid_count += 1

                # Batch commit every 500 records
                if (i + 1) % 500 == 0:
                    db.commit()
                    logger.info(f"Processed {i + 1}/{total} records")

            except Exception as e:
                invalid_count += 1
                logger.warning(f"Error processing record {i + 1}: {e}")
                try:
                    raw_err = RawRecord(
                        dataset_id=dataset.id,
                        line_number=i + 1,
                        raw_data=rec if isinstance(rec, dict) else {"raw": str(rec)},
                        is_valid=False,
                        error_message=str(e)
                    )
                    db.add(raw_err)
                except Exception:
                    pass

        dataset.valid_records = valid_count
        dataset.invalid_records = invalid_count
        dataset.duplicate_records = duplicate_count
        dataset.status = "COMPLETED"
        db.commit()

        logger.info(
            f"Dataset {dataset_id} processed: {valid_count} valid, "
            f"{invalid_count} invalid, {duplicate_count} duplicates out of {total} total"
        )

    except Exception as e:
        dataset.status = "FAILED"
        db.commit()
        logger.error(f"Dataset {dataset_id} processing failed: {e}")
        raise
    finally:
        db.expire_on_commit = orig_expire


import zipfile
import tempfile
import os
import gc

def process_relational_bundle_async(dataset_id: int, bundle_source: Union[bytes, str], job_id: Optional[str] = None):
    """
    Background worker function for streaming relational dataset bundle ingestion.
    Executes in a detached thread with its own SQLAlchemy session.
    Accepts either raw bytes or a disk file path (recommended for low memory).
    Dependency order:
    1. Wallets (btc_shield_wallets.csv)
    2. Transactions & Network (btc_shield_transactions_100000.csv)
    3. Edges (btc_shield_edges_100000.csv)
    4. Enrichment (btc_shield_enrichment_100000.csv)
    """
    from app.core.database import SessionLocal
    from app.services import job_service
    from app.models.models import GraphEdge, RawRecord

    db = SessionLocal()
    orig_expire = db.expire_on_commit
    db.expire_on_commit = False

    try:
        if job_id:
            job_service.update_job(job_id, "PROCESSING", 5, "Extracting relational archive...")

        dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            logger.error(f"Dataset {dataset_id} not found in background ingestion.")
            return

        zip_target = bundle_source if isinstance(bundle_source, str) else io.BytesIO(bundle_source)
        with zipfile.ZipFile(zip_target, "r") as z:
            namelist = z.namelist()

            wallets_fname = next((n for n in namelist if "wallets" in n.lower() and n.endswith(".csv")), None)
            tx_fname = next((n for n in namelist if "transactions" in n.lower() and n.endswith(".csv")), None)
            edges_fname = next((n for n in namelist if "edges" in n.lower() and n.endswith(".csv")), None)
            enrich_fname = next((n for n in namelist if "enrichment" in n.lower() and n.endswith(".csv")), None)

            # 1. Wallets (45,000)
            if wallets_fname:
                if job_id:
                    job_service.update_job(job_id, "PROCESSING", 15, "Ingesting wallet entities...")
                with z.open(wallets_fname) as wf:
                    w_lines = io.TextIOWrapper(wf, encoding="utf-8")
                    reader = csv.DictReader(w_lines)
                    w_batch = []
                    for row in reader:
                        addr = row.get("address")
                        if not addr:
                            continue
                        w = Wallet(
                            address=addr,
                            wallet_type=row.get("wallet_type"),
                            country=row.get("country"),
                            synthetic_balance_sats=safe_float(row.get("synthetic_balance_sats")),
                            tx_count=int(safe_float(row.get("observed_transaction_count"))),
                            total_sent=0.0,
                            total_received=0.0
                        )
                        w_batch.append(w)
                        if len(w_batch) >= 5000:
                            db.bulk_save_objects(w_batch)
                            db.commit()
                            w_batch = []
                    if w_batch:
                        db.bulk_save_objects(w_batch)
                        db.commit()

            # 2. Transactions & Network Observations (100,000)
            if tx_fname:
                if job_id:
                    job_service.update_job(job_id, "PROCESSING", 40, "Ingesting 100,000 transactions and network observations...")
                with z.open(tx_fname) as tf:
                    t_lines = io.TextIOWrapper(tf, encoding="utf-8")
                    reader = csv.DictReader(t_lines)
                    tx_batch = []
                    net_batch = []
                    raw_batch = []

                    line_no = 0
                    valid_tx = 0
                    for row in reader:
                        line_no += 1
                        txid = row.get("txid")
                        if not txid:
                            continue

                        ts = normalize_timestamp(row.get("timestamp"))
                        in_amts = parse_amount_list(row.get("input_amounts"))
                        out_amts = parse_amount_list(row.get("output_amounts"))
                        tin = sum(in_amts)
                        tout = sum(out_amts)
                        fee = calculate_fee(row.get("fee"), tin, tout)

                        tx = Transaction(
                            dataset_id=dataset.id,
                            txid=txid,
                            timestamp=ts,
                            fee=fee,
                            script_type=row.get("script_type"),
                            total_input=tin,
                            total_output=tout
                        )
                        tx_batch.append(tx)

                        src_ip = row.get("src_ip", "")
                        if src_ip:
                            net = NetworkObservation(
                                dataset_id=dataset.id,
                                transaction_id=txid,
                                src_ip=src_ip,
                                dst_ip=row.get("dst_ip", ""),
                                src_port=int(safe_float(row.get("src_port"))),
                                dst_port=int(safe_float(row.get("dst_port"))),
                                timestamp=ts,
                                geo_country=row.get("geo_country", ""),
                                asn=row.get("asn", "")
                            )
                            net_batch.append(net)

                        # RawRecord for audit
                        raw = RawRecord(
                            dataset_id=dataset.id,
                            line_number=line_no,
                            raw_data=row,
                            is_valid=True
                        )
                        raw_batch.append(raw)
                        valid_tx += 1

                        if len(tx_batch) >= 5000:
                            db.bulk_save_objects(tx_batch)
                            db.bulk_save_objects(net_batch)
                            db.bulk_save_objects(raw_batch)
                            db.commit()
                            tx_batch, net_batch, raw_batch = [], [], []

                    if tx_batch:
                        db.bulk_save_objects(tx_batch)
                        db.bulk_save_objects(net_batch)
                        db.bulk_save_objects(raw_batch)
                        db.commit()

                    dataset.total_records = line_no
                    dataset.valid_records = valid_tx
                    dataset.invalid_records = 0
                    db.commit()

            # 3. Edges (350,131)
            if edges_fname:
                if job_id:
                    job_service.update_job(job_id, "PROCESSING", 70, "Ingesting 350,131 graph edges...")
                with z.open(edges_fname) as ef:
                    e_lines = io.TextIOWrapper(ef, encoding="utf-8")
                    reader = csv.DictReader(e_lines)
                    edge_batch = []
                    for row in reader:
                        ge = GraphEdge(
                            source_type="TRANSACTION",
                            source_id=row.get("source_txid"),
                            target_type="TRANSACTION",
                            target_id=row.get("target_txid"),
                            edge_type=row.get("edge_type", "MONEY_FLOW"),
                            weight=1.0,
                            properties={"wallet_address": row.get("wallet_address")},
                            provenance="SYNTHETIC_100K"
                        )
                        edge_batch.append(ge)
                        if len(edge_batch) >= 10000:
                            db.bulk_save_objects(edge_batch)
                            db.commit()
                            edge_batch = []
                    if edge_batch:
                        db.bulk_save_objects(edge_batch)
                        db.commit()

            # 4. Enrichment (100,000)
            if enrich_fname:
                if job_id:
                    job_service.update_job(job_id, "PROCESSING", 90, "Ingesting enrichment and ground-truth metadata...")
                with z.open(enrich_fname) as enf:
                    en_lines = io.TextIOWrapper(enf, encoding="utf-8")
                    reader = csv.DictReader(en_lines)
                    en_batch = []
                    line_no = 0
                    for row in reader:
                        line_no += 1
                        raw = RawRecord(
                            dataset_id=dataset.id,
                            line_number=line_no,
                            raw_data=row,
                            is_valid=True
                        )
                        en_batch.append(raw)
                        if len(en_batch) >= 10000:
                            db.bulk_save_objects(en_batch)
                            db.commit()
                            en_batch = []
                    if en_batch:
                        db.bulk_save_objects(en_batch)
                        db.commit()

        dataset.status = "COMPLETED"
        db.commit()

        if job_id:
            job_service.update_job(
                job_id,
                "COMPLETED",
                100,
                "Relational dataset 100K ingestion successfully finished!",
                result={"dataset_id": dataset.id, "total_records": dataset.total_records}
            )

        logger.info(f"Relational dataset bundle {dataset_id} completed successfully.")

    except Exception as e:
        logger.error(f"Relational bundle processing failed for dataset {dataset_id}: {e}")
        try:
            dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
            if dataset:
                dataset.status = "FAILED"
                db.commit()
        except Exception:
            pass
        if job_id:
            job_service.update_job(job_id, "FAILED", 0, f"Ingestion error: {str(e)}")
    finally:
        db.expire_on_commit = orig_expire
        db.close()
        if isinstance(bundle_source, str) and os.path.exists(bundle_source):
            try:
                os.remove(bundle_source)
            except Exception:
                pass
        gc.collect()
