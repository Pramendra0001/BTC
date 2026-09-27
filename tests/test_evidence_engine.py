import pytest
from app.services.ingestion_service import process_dataset
from app.services.feature_service import compute_all_features
from app.services.ml_service import run_full_ml_pipeline
from app.services.evidence_service import generate_evidence
from app.models.models import Dataset, Evidence

def test_evidence_generation(db_session):
    ds = Dataset(name="ev_test.csv", filename="ev_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    # Create bursty high fan-out transactions
    csv_rows = ["txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn"]
    for i in range(12):
        csv_rows.append(
            f"tx_ev_{i},2026-03-01T10:{i:02d}:00Z,500,p2pkh,wallet_target_alpha,out_addr_{i},50000,49500,10.0.0.{i+1},10.0.0.100,8333,8333,US,AS15169"
        )
    csv_data = "\n".join(csv_rows).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    compute_all_features(db_session)
    run_full_ml_pipeline(db_session, ds.id)
    ev_count = generate_evidence(db_session)

    assert ev_count > 0

    evidences = db_session.query(Evidence).all()
    assert len(evidences) > 0

    # Ensure each evidence has valid category, observation, strength
    for e in evidences:
        assert e.category in ["MODEL", "CLUSTER", "AMOUNT", "TRANSACTION", "TEMPORAL", "NETWORK", "GEOGRAPHIC", "GRAPH"]
        assert len(e.observation) > 10
        assert 0.0 <= e.strength <= 1.0


def test_evidence_regeneration_with_case_evidence_rerun(db_session):
    """
    Verifies that rerunning the evidence generation pipeline on an existing database
    with active Cases and CaseEvidence associations does NOT raise ForeignKeyViolation.
    """
    from app.models.models import Case, CaseEvidence, User
    
    # 1. First run
    ds = Dataset(name="rerun_test.csv", filename="rerun_test.csv", format="csv")
    db_session.add(ds)
    db_session.commit()

    csv_rows = ["txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn"]
    for i in range(5):
        csv_rows.append(
            f"tx_rerun_{i},2026-03-01T12:{i:02d}:00Z,500,p2pkh,addr_rerun_src,addr_rerun_dst_{i},50000,49500,10.0.0.{i+1},10.0.0.50,8333,8333,US,AS15169"
        )
    csv_data = "\n".join(csv_rows).encode("utf-8")

    process_dataset(db_session, ds.id, csv_data)
    compute_all_features(db_session)
    run_full_ml_pipeline(db_session, ds.id)
    ev_count = generate_evidence(db_session)
    assert ev_count > 0

    first_evidence = db_session.query(Evidence).first()
    assert first_evidence is not None

    # Attach this evidence to a case (simulating investigator action or prior run)
    user = db_session.query(User).first()
    user_id = user.id if user else None
    case = Case(title="Rerun Test Case", description="Testing FK cascade resilience", investigator_id=user_id)
    db_session.add(case)
    db_session.commit()

    case_ev = CaseEvidence(case_id=case.id, evidence_id=first_evidence.id)
    db_session.add(case_ev)
    db_session.commit()

    # Verify link exists
    assert db_session.query(CaseEvidence).count() >= 1

    # 2. Second run: Trigger regeneration of evidence on the exact same database session
    # Must succeed without ForeignKeyViolation
    rerun_ev_count = generate_evidence(db_session)
    assert rerun_ev_count > 0
    assert db_session.query(Evidence).count() == rerun_ev_count

