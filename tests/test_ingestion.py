import pytest
import json
from app.services.ingestion_service import (
    validate_ip, validate_bitcoin_address, normalize_timestamp,
    process_dataset, detect_format, parse_address_list,
    parse_amount_list, calculate_fee
)
from app.models.models import (
    Dataset, Transaction, TransactionInput, TransactionOutput,
    Wallet, IPEntity, ASNEntity, NetworkObservation, RawRecord
)

def test_ip_validation():
    assert validate_ip("192.168.1.1") is True
    assert validate_ip("10.0.0.255") is True
    assert validate_ip("256.1.1.1") is False
    assert validate_ip("not_an_ip") is False
    assert validate_ip("") is False

def test_bitcoin_address_validation():
    assert validate_bitcoin_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa") is True
    assert validate_bitcoin_address("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy") is True
    assert validate_bitcoin_address("bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq") is True
    assert validate_bitcoin_address("too_short") is False

def test_detect_format():
    assert detect_format("transactions.csv") == "csv"
    assert detect_format("dump.json") == "json"
    assert detect_format("feed.xml") == "xml"
    assert detect_format("unknown.txt") == "unknown"

def test_csv_ingestion_and_normalization(db_session):
    ds = Dataset(name="test.csv", filename="test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    csv_data = (
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn\n"
        "tx_test_001,2026-03-01T10:00:00Z,500,p2pkh,1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa,1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2,50000,49500,192.168.1.50,192.168.1.1,8333,8333,US,AS15169\n"
        "tx_test_002,2026-03-01T10:05:00Z,600,p2pkh,1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2,1CounterpartyAddr01,49500,48900,192.168.1.50,10.0.0.1,8333,8333,US,AS15169\n"
    ).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 2
    assert ds.valid_records == 2
    assert ds.invalid_records == 0

    # Verify transactions created
    txs = db_session.query(Transaction).filter(Transaction.dataset_id == ds.id).all()
    assert len(txs) == 2

    # Verify wallet entities created
    wallets = db_session.query(Wallet).all()
    assert len(wallets) >= 2

    # Verify IP entities created
    ips = db_session.query(IPEntity).all()
    assert any(ip.ip_address == "192.168.1.50" for ip in ips)

def test_duplicate_record_handling(db_session):
    ds = Dataset(name="dupes.csv", filename="dupes.csv", format="csv")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    csv_with_dupes = (
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn\n"
        "tx_dupe_01,2026-03-01T10:00:00Z,500,p2pkh,1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa,1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2,50000,49500,192.168.1.50,192.168.1.1,8333,8333,US,AS15169\n"
        "tx_dupe_01,2026-03-01T10:00:00Z,500,p2pkh,1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa,1BvBMSEYstWetqTFn5Au4m4GFg7xJaNVN2,50000,49500,192.168.1.50,192.168.1.1,8333,8333,US,AS15169\n"
    ).encode("utf-8")

    process_dataset(db_session, ds.id, csv_with_dupes)
    db_session.refresh(ds)

    assert ds.duplicate_records == 1
    assert ds.valid_records == 1

def test_json_ingestion_and_normalization(db_session):
    ds = Dataset(name="dump.json", filename="dump.json", format="json")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    json_payload = [
        {
            "txid": "tx_json_001",
            "timestamp": "2026-03-01T12:00:00Z",
            "fee": 250,
            "script_type": "p2wpkh",
            "input_addresses": "bc1qjsonaddr01",
            "output_addresses": "bc1qjsonaddr02",
            "input_amounts": "100000",
            "output_amounts": "99750",
            "src_ip": "198.51.100.10",
            "dst_ip": "198.51.100.1",
            "src_port": 8333,
            "dst_port": 8333,
            "geo_country": "DE",
            "asn": "AS24940"
        }
    ]
    json_bytes = json.dumps(json_payload).encode("utf-8")

    process_dataset(db_session, ds.id, json_bytes)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 1
    assert ds.valid_records == 1
    assert ds.invalid_records == 0

    tx = db_session.query(Transaction).filter(Transaction.txid == "tx_json_001").first()
    assert tx is not None
    assert tx.fee == 250

def test_xml_ingestion_and_normalization(db_session):
    ds = Dataset(name="feed.xml", filename="feed.xml", format="xml")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    xml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<records>\n'
        '  <record>\n'
        '    <txid>tx_xml_001</txid>\n'
        '    <timestamp>2026-03-01T14:30:00Z</timestamp>\n'
        '    <fee>400</fee>\n'
        '    <script_type>p2pkh</script_type>\n'
        '    <input_addresses>1XmlSourceAddress01</input_addresses>\n'
        '    <output_addresses>1XmlDestAddress01</output_addresses>\n'
        '    <input_amounts>75000</input_amounts>\n'
        '    <output_amounts>74600</output_amounts>\n'
        '    <src_ip>203.0.113.5</src_ip>\n'
        '    <dst_ip>203.0.113.1</dst_ip>\n'
        '    <src_port>8333</src_port>\n'
        '    <dst_port>8333</dst_port>\n'
        '    <geo_country>CH</geo_country>\n'
        '    <asn>AS13030</asn>\n'
        '  </record>\n'
        '</records>'
    ).encode("utf-8")

    process_dataset(db_session, ds.id, xml_content)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 1
    assert ds.valid_records == 1
    assert ds.invalid_records == 0

    tx = db_session.query(Transaction).filter(Transaction.txid == "tx_xml_001").first()
    assert tx is not None
    assert tx.fee == 400

def test_malformed_record_quarantine(db_session):
    ds = Dataset(name="malformed.csv", filename="malformed.csv", format="csv")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    malformed_csv = (
        "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn\n"
        ",2026-03-01T10:00:00Z,500,p2pkh,1Addr01,1Addr02,5000,4500,192.168.1.1,10.0.0.1,8333,8333,US,AS123\n" # missing txid
        "tx_bad_ip,2026-03-01T10:05:00Z,500,p2pkh,1Addr01,1Addr02,5000,4500,999.999.999.999,10.0.0.1,8333,8333,US,AS123\n" # invalid src_ip
    ).encode("utf-8")

    process_dataset(db_session, ds.id, malformed_csv)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 2
    assert ds.invalid_records == 2
    assert ds.valid_records == 0

def test_polyglot_address_parsing():
    """Verify parsing of native lists, JSON-stringified arrays, and semicolon/comma strings."""
    # Native lists
    assert parse_address_list(["SYNW_001", "SYNW_002"]) == ["SYNW_001", "SYNW_002"]
    # JSON-stringified arrays
    assert parse_address_list('["SYNW_001", "SYNW_002"]') == ["SYNW_001", "SYNW_002"]
    # Python literal repr
    assert parse_address_list("['SYNW_001', 'SYNW_002']") == ["SYNW_001", "SYNW_002"]
    # Semicolon-separated legacy strings
    assert parse_address_list("1AddrA;1AddrB") == ["1AddrA", "1AddrB"]
    # Single address
    assert parse_address_list("1AddrSolo") == ["1AddrSolo"]
    # Empty and None
    assert parse_address_list("") == []
    assert parse_address_list(None) == []

def test_polyglot_amount_parsing():
    """Verify parsing of BTC decimals, legacy satoshis, multi-value arrays, and scalars."""
    # Native float lists
    assert parse_amount_list([3.17790883, 0.5]) == [3.17790883, 0.5]
    # JSON string arrays
    assert parse_amount_list("[3.17790883, 0.5]") == [3.17790883, 0.5]
    # Legacy semicolon-separated strings (satoshis or integers)
    assert parse_amount_list("100000;50000") == [100000.0, 50000.0]
    # Semicolon-separated BTC decimals
    assert parse_amount_list("3.17790883;0.5") == [3.17790883, 0.5]
    # Single numbers
    assert parse_amount_list(100000) == [100000.0]
    assert parse_amount_list(3.17790883) == [3.17790883]
    # Empty and None
    assert parse_amount_list("") == []
    assert parse_amount_list(None) == []

def test_fee_calculation_rules():
    """Verify explicit fee preservation, missing fee computation, and zero-fee preservation."""
    # Explicit fee preserved
    assert calculate_fee(500, 1000.0, 500.0) == 500.0
    assert calculate_fee("0.0005", 1.0, 0.9995) == 0.0005
    # Explicit zero fee preserved
    assert calculate_fee(0, 10.0, 5.0) == 0.0
    assert calculate_fee("0", 10.0, 5.0) == 0.0
    # Missing fee computed from total_input - total_output
    assert calculate_fee(None, 3.17790883, 3.17155301) == 0.00635582
    assert calculate_fee("", 100.0, 95.0) == 5.0
    # Negative clamp to 0.0
    assert calculate_fee(None, 5.0, 10.0) == 0.0

def test_canonical_csv_format_ingestion(db_session):
    """Test ingestion of canonical CSV format matching btc_shield_synthetic_transactions.csv."""
    ds = Dataset(name="canonical_test.csv", filename="canonical_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    csv_data = (
        'txid,timestamp,src_ip,dst_ip,src_port,dst_port,input_addresses,output_addresses,input_amounts,output_amounts,geo_country,asn,scenario\n'
        '20c45cbef029ea3f53da5c41a67828909b5ce89123ae95cf51a71b321f475707,2026-01-01T00:17:00Z,198.51.100.2,198.51.100.9,23128,18333,"[""SYNW_88b25ebd15621261264ec8685ff73a34""]","[""SYNW_3d2b0d52d9583ab02283dfdbc99e3da4""]","[3.17790883]","[3.17155301]",US,AS-SYN-US,normal_baseline\n'
        '2936e50c1852dd2d27c212dfccd9164ea028a8b6cfebffd05f5527b6aee70220,2026-01-01T00:34:00Z,198.51.100.3,198.51.100.10,43972,18333,"[""SYNW_3d2b0d52d9583ab02283dfdbc99e3da4""]","[""SYNW_fbbb82e9906a723248f348903e607e6f""]","[0.37996613]","[0.3792062]",DE,AS-SYN-DE,normal_baseline\n'
    ).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 2
    assert ds.valid_records == 2
    assert ds.invalid_records == 0

    tx1 = db_session.query(Transaction).filter(Transaction.txid == "20c45cbef029ea3f53da5c41a67828909b5ce89123ae95cf51a71b321f475707").first()
    assert tx1 is not None
    assert round(tx1.total_input, 8) == 3.17790883
    assert round(tx1.total_output, 8) == 3.17155301
    assert round(tx1.fee, 8) == 0.00635582  # computed dynamically from total_input - total_output

    # Verify input/output models
    ti = db_session.query(TransactionInput).filter(TransactionInput.transaction_id == tx1.id).first()
    assert ti.wallet_address == "SYNW_88b25ebd15621261264ec8685ff73a34"
    assert round(ti.amount, 8) == 3.17790883

    to = db_session.query(TransactionOutput).filter(TransactionOutput.transaction_id == tx1.id).first()
    assert to.wallet_address == "SYNW_3d2b0d52d9583ab02283dfdbc99e3da4"
    assert round(to.amount, 8) == 3.17155301

    # Verify network observation
    obs = db_session.query(NetworkObservation).filter(NetworkObservation.transaction_id == tx1.txid).first()
    assert obs.src_ip == "198.51.100.2"
    assert obs.geo_country == "US"
    assert obs.asn == "AS-SYN-US"

def test_canonical_json_format_ingestion(db_session):
    """Test ingestion of canonical JSON format matching btc_shield_synthetic_transactions.json."""
    ds = Dataset(name="canonical_test.json", filename="canonical_test.json", format="json")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    json_data = json.dumps([
        {
            "txid": "canonical_json_tx_01",
            "timestamp": "2026-01-01T01:00:00Z",
            "src_ip": "198.51.100.4",
            "dst_ip": "198.51.100.11",
            "src_port": 26891,
            "dst_port": 8333,
            "input_addresses": ["SYNW_fbbb82e9906a723248f348903e607e6f"],
            "output_addresses": ["SYNW_b5df4d74066f071593344bbbf14b0c82"],
            "input_amounts": [0.66258975],
            "output_amounts": [0.66126457],
            "geo_country": "SG",
            "asn": "AS-SYN-SG",
            "scenario": "peeling_chain"
        }
    ]).encode("utf-8")

    process_dataset(db_session, ds.id, json_data)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 1
    assert ds.valid_records == 1

    tx = db_session.query(Transaction).filter(Transaction.txid == "canonical_json_tx_01").first()
    assert tx is not None
    assert round(tx.fee, 8) == 0.00132518

def test_canonical_xml_format_ingestion(db_session):
    """Test ingestion of canonical XML format matching btc_shield_synthetic_transactions.xml."""
    ds = Dataset(name="canonical_test.xml", filename="canonical_test.xml", format="xml")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    xml_data = (
        "<?xml version='1.0' encoding='utf-8'?>\n"
        "<btc_shield_dataset>"
        "<transaction>"
        "<timestamp>2026-01-01T01:08:00Z</timestamp>"
        "<src_ip>198.51.100.5</src_ip>"
        "<dst_ip>198.51.100.12</dst_ip>"
        "<src_port>21271</src_port>"
        "<dst_port>18333</dst_port>"
        "<txid>canonical_xml_tx_01</txid>"
        "<input_addresses>[\"SYNW_b5df4d74066f071593344bbbf14b0c82\"]</input_addresses>"
        "<output_addresses>[\"SYNW_8df464d057d4b01d9074eae9dd9dc635\"]</output_addresses>"
        "<input_amounts>[2.46160789]</input_amounts>"
        "<output_amounts>[2.45668467]</output_amounts>"
        "<geo_country>GB</geo_country>"
        "<asn>AS-SYN-GB</asn>"
        "<scenario>normal_baseline</scenario>"
        "</transaction>"
        "</btc_shield_dataset>"
    ).encode("utf-8")

    process_dataset(db_session, ds.id, xml_data)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 1
    assert ds.valid_records == 1

    tx = db_session.query(Transaction).filter(Transaction.txid == "canonical_xml_tx_01").first()
    assert tx is not None
    assert round(tx.total_input, 8) == 2.46160789
    assert round(tx.total_output, 8) == 2.45668467

def test_scenario_field_preservation_and_no_leakage(db_session):
    """Verify that scenario metadata is preserved in RawRecord but never stored as a column on Transaction/Wallet."""
    ds = Dataset(name="scenario_test.json", filename="scenario_test.json", format="json")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    json_data = json.dumps([
        {
            "txid": "scenario_tx_999",
            "timestamp": "2026-01-01T02:00:00Z",
            "input_addresses": ["SYNW_source"],
            "output_addresses": ["SYNW_dest"],
            "input_amounts": [1.0],
            "output_amounts": [0.99],
            "scenario": "ransomware_payment_chain"
        }
    ]).encode("utf-8")

    process_dataset(db_session, ds.id, json_data)
    db_session.refresh(ds)

    # 1. RawRecord preserves the raw ground-truth evaluation metadata
    raw = db_session.query(RawRecord).filter(RawRecord.dataset_id == ds.id).first()
    assert raw is not None
    assert raw.raw_data.get("scenario") == "ransomware_payment_chain"

    # 2. Transaction model does NOT have a scenario column
    tx = db_session.query(Transaction).filter(Transaction.txid == "scenario_tx_999").first()
    assert tx is not None
    assert not hasattr(tx, "scenario")

    # 3. Wallet model does NOT have a scenario column
    wallet = db_session.query(Wallet).filter(Wallet.address == "SYNW_source").first()
    assert wallet is not None
    assert not hasattr(wallet, "scenario")


