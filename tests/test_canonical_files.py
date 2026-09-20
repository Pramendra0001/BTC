import pytest
import os
import json
from app.services.ingestion_service import process_dataset
from app.models.models import Dataset, Transaction, Wallet, IPEntity, RawRecord

def get_sample_path(filename: str) -> str:
    """Get path to data/samples file without hardcoding absolute paths."""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "data", "samples", filename)

def test_canonical_1000_csv_full_ingestion(db_session):
    """Test full ingestion of canonical 1,000-record CSV dataset."""
    path = get_sample_path("btc_shield_synthetic_transactions.csv")
    if not os.path.exists(path):
        pytest.skip("Canonical CSV file not present")

    with open(path, "rb") as f:
        csv_bytes = f.read()

    ds = Dataset(name="canonical_1000.csv", filename="btc_shield_synthetic_transactions.csv", format="csv")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    process_dataset(db_session, ds.id, csv_bytes)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 1000
    assert ds.valid_records == 1000
    assert ds.invalid_records == 0
    assert ds.duplicate_records == 0

    tx_count = db_session.query(Transaction).filter(Transaction.dataset_id == ds.id).count()
    assert tx_count == 1000

def test_canonical_1000_json_full_ingestion(db_session):
    """Test full ingestion of canonical 1,000-record JSON dataset."""
    path = get_sample_path("btc_shield_synthetic_transactions.json")
    if not os.path.exists(path):
        pytest.skip("Canonical JSON file not present")

    with open(path, "rb") as f:
        json_bytes = f.read()

    ds = Dataset(name="canonical_1000.json", filename="btc_shield_synthetic_transactions.json", format="json")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    process_dataset(db_session, ds.id, json_bytes)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 1000
    assert ds.valid_records == 1000
    assert ds.invalid_records == 0

def test_canonical_1000_xml_full_ingestion(db_session):
    """Test full ingestion of canonical 1,000-record XML dataset."""
    path = get_sample_path("btc_shield_synthetic_transactions.xml")
    if not os.path.exists(path):
        pytest.skip("Canonical XML file not present")

    with open(path, "rb") as f:
        xml_bytes = f.read()

    ds = Dataset(name="canonical_1000.xml", filename="btc_shield_synthetic_transactions.xml", format="xml")
    db_session.add(ds)
    db_session.commit()
    db_session.refresh(ds)

    process_dataset(db_session, ds.id, xml_bytes)
    db_session.refresh(ds)

    assert ds.status == "COMPLETED"
    assert ds.total_records == 1000
    assert ds.valid_records == 1000
    assert ds.invalid_records == 0
