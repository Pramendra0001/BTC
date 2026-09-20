import pytest
import json
from app.services.ingestion_service import (
    validate_ip, validate_bitcoin_address, normalize_timestamp,
    process_dataset, detect_format
)
from app.models.models import Dataset, Transaction, Wallet, IPEntity, RawRecord

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

