"""
BTC-SHIELD — Persistent Database Rerun Verification Script
Proves that the complete forensic intelligence pipeline can execute repeatedly
against an active database with existing Cases, CaseEvidence, and Evidence without
encountering ForeignKeyViolation or constraint errors.
"""
import sys
import os

sys.path.insert(0, os.path.abspath("backend"))

from app.core.database import SessionLocal, engine, Base
from app.models.models import Dataset, Case, CaseEvidence, Evidence, User
from app.services.ingestion_service import process_dataset
from app.services.feature_service import compute_all_features
from app.services.ml_service import run_full_ml_pipeline
from app.services.evidence_service import generate_evidence
from app.services.alert_service import generate_alerts
from app.services.graph_service import build_graph, compute_centrality

def run_pipeline_cycle(cycle_num: int):
    print(f"\n[+] STARTING PIPELINE EXECUTION CYCLE #{cycle_num}...")
    db = SessionLocal()
    try:
        # 1. Ingest dataset
        dataset_name = f"persistent_test_cycle_{cycle_num}.csv"
        ds = Dataset(name=dataset_name, filename=dataset_name, format="csv")
        db.add(ds)
        db.commit()
        db.refresh(ds)

        csv_rows = [
            "txid,timestamp,fee,script_type,input_addresses,output_addresses,input_amounts,output_amounts,src_ip,dst_ip,src_port,dst_port,geo_country,asn"
        ]
        for i in range(10):
            csv_rows.append(
                f"tx_cycle_{cycle_num}_{i:02d},2026-03-01T14:{i:02d}:00Z,500,p2pkh,src_wallet_{cycle_num},dst_wallet_{cycle_num}_{i},100000,99500,192.0.2.{i+1},198.51.100.1,8333,8333,US,AS15169"
            )
        csv_data = "\n".join(csv_rows).encode("utf-8")

        print(f"    - Processing dataset {ds.id}...")
        process_dataset(db, ds.id, csv_data)

        print("    - Computing 23-dimensional behavioral features...")
        compute_all_features(db)

        print("    - Running ML pipeline (Isolation Forest + DBSCAN)...")
        run_full_ml_pipeline(db, ds.id)

        print("    - Building graph and computing centrality...")
        G = build_graph(db)
        compute_centrality(G)

        print("    - Generating multi-signal evidence...")
        ev_count = generate_evidence(db)
        print(f"      Generated {ev_count} evidence items.")

        print("    - Generating prioritized alerts...")
        generate_alerts(db)

        # Attach evidence to an investigative case to test foreign key constraints on rerun
        admin = db.query(User).first()
        admin_id = admin.id if admin else None
        case = Case(
            title=f"Cycle {cycle_num} Forensic Case",
            description=f"Automated case created in cycle {cycle_num}",
            priority="HIGH",
            investigator_id=admin_id
        )
        db.add(case)
        db.commit()
        db.refresh(case)

        latest_ev = db.query(Evidence).first()
        if latest_ev:
            case_ev = CaseEvidence(case_id=case.id, evidence_id=latest_ev.id)
            db.add(case_ev)
            db.commit()
            print(f"      Linked Evidence {latest_ev.id} to Case {case.id} (case_evidence entry created).")

        print(f"[OK] CYCLE #{cycle_num} COMPLETED SUCCESSFULLY WITH ZERO ERRORS.")
        return True
    except Exception as e:
        print(f"[FAIL] CYCLE #{cycle_num} FAILED WITH ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()

def main():
    print("=================================================================")
    print("   BTC-SHIELD — PERSISTENT DATABASE REPEATABILITY VERIFIER       ")
    print("=================================================================")
    Base.metadata.create_all(bind=engine)

    # RUN 1
    success_1 = run_pipeline_cycle(1)
    if not success_1:
        print("\n[!] Run 1 Failed. Aborting.")
        sys.exit(1)

    # RUN 2 on the exact same database without resetting or dropping
    success_2 = run_pipeline_cycle(2)
    if not success_2:
        print("\n[!] Run 2 Failed with Foreign Key or Database Error.")
        sys.exit(1)

    print("\n=================================================================")
    print("PERSISTENT DATABASE VERIFICATION RESULTS:")
    print("  RUN 1: PASS")
    print("  RUN 2: PASS (Zero ForeignKeyViolation, clean evidence regeneration)")
    print("=================================================================")

if __name__ == "__main__":
    main()
