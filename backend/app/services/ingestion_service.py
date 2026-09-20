"""
BTC-SHIELD Ingestion Service
Multi-format data ingestion with validation, normalization, and quality tracking.
"""
import json
import csv
import io
import xml.etree.ElementTree as ET
from sqlalchemy.orm import Session
from app.models.models import (
    Dataset, RawRecord, Transaction, TransactionInput, TransactionOutput,
    NetworkObservation, Wallet, IPEntity, ASNEntity
)
from datetime import datetime
from typing import Optional
import re
import logging
import hashlib

logger = logging.getLogger(__name__)

# --- Validation Helpers ---

def validate_ip(ip: str) -> bool:
    """Validate IPv4 address format."""
    if not ip:
        return False
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
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

                # Parse semicolon-separated fields
                input_addrs = [a.strip() for a in rec.get("input_addresses", "").split(";") if a.strip()]
                output_addrs = [a.strip() for a in rec.get("output_addresses", "").split(";") if a.strip()]
                input_amts = [safe_float(a) for a in rec.get("input_amounts", "").split(";") if a.strip()]
                output_amts = [safe_float(a) for a in rec.get("output_amounts", "").split(";") if a.strip()]

                total_input = sum(input_amts) if input_amts else 0
                total_output = sum(output_amts) if output_amts else 0
                fee = safe_float(rec.get("fee", 0))

                # Create or get transaction
                existing_tx = db.query(Transaction).filter(Transaction.txid == rec["txid"]).first()
                if existing_tx:
                    tx = existing_tx
                else:
                    tx = Transaction(
                        dataset_id=dataset.id,
                        txid=rec["txid"],
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
                        amt = input_amts[pos] if pos < len(input_amts) else 0
                        ti = TransactionInput(
                            transaction_id=tx.id,
                            wallet_address=addr,
                            amount=amt,
                            position=pos
                        )
                        db.add(ti)

                    # Create transaction outputs
                    for pos, addr in enumerate(output_addrs):
                        amt = output_amts[pos] if pos < len(output_amts) else 0
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
                        wallet = db.query(Wallet).filter(Wallet.address == addr).first()
                        if not wallet:
                            wallet = Wallet(
                                address=addr,
                                first_seen=ts,
                                last_seen=ts,
                                total_sent=0,
                                total_received=0,
                                tx_count=0
                            )
                            db.add(wallet)
                            db.flush()

                        # Update wallet stats
                        wallet.tx_count = (wallet.tx_count or 0) + 1
                        if ts and (wallet.last_seen is None or ts > wallet.last_seen):
                            wallet.last_seen = ts
                        if ts and (wallet.first_seen is None or ts < wallet.first_seen):
                            wallet.first_seen = ts

                        if addr in input_addrs:
                            idx = input_addrs.index(addr)
                            amt = input_amts[idx] if idx < len(input_amts) else 0
                            wallet.total_sent = (wallet.total_sent or 0) + amt
                        if addr in output_addrs:
                            idx = output_addrs.index(addr)
                            amt = output_amts[idx] if idx < len(output_amts) else 0
                            wallet.total_received = (wallet.total_received or 0) + amt

                # Create network observation
                if rec.get("src_ip"):
                    net_obs = NetworkObservation(
                        dataset_id=dataset.id,
                        transaction_id=rec["txid"],
                        src_ip=rec.get("src_ip", ""),
                        dst_ip=rec.get("dst_ip", ""),
                        src_port=int(rec.get("src_port", 0)) if rec.get("src_port") else None,
                        dst_port=int(rec.get("dst_port", 0)) if rec.get("dst_port") else None,
                        timestamp=ts,
                        geo_country=rec.get("geo_country", ""),
                        asn=rec.get("asn", "")
                    )
                    db.add(net_obs)

                    # Resolve IP entity
                    ip_ent = db.query(IPEntity).filter(IPEntity.ip_address == rec["src_ip"]).first()
                    if not ip_ent:
                        ip_ent = IPEntity(
                            ip_address=rec["src_ip"],
                            first_seen=ts,
                            last_seen=ts,
                            observation_count=0,
                            asn=rec.get("asn", ""),
                            country=rec.get("geo_country", "")
                        )
                        db.add(ip_ent)
                    ip_ent.observation_count = (ip_ent.observation_count or 0) + 1
                    if ts and (ip_ent.last_seen is None or ts > ip_ent.last_seen):
                        ip_ent.last_seen = ts

                    # Resolve ASN entity
                    asn_val = rec.get("asn", "")
                    if asn_val:
                        asn_ent = db.query(ASNEntity).filter(ASNEntity.asn_number == asn_val).first()
                        if not asn_ent:
                            asn_ent = ASNEntity(
                                asn_number=asn_val,
                                name=f"ASN {asn_val}",
                                country_count=0,
                                ip_count=0
                            )
                            db.add(asn_ent)

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
