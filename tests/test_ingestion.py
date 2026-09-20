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
