"""
BTC-SHIELD Final Release Validation Tests
Verifies graph prefix normalization, heuristics dual-schema extraction,
alert detail response schema compatibility, and presentation case seeding.
"""
import pytest
from app.services.graph_service import normalize_entity_key, get_subgraph, get_default_graph_entity
from app.services.heuristics_service import detect_peeling_chains, detect_mixing_patterns, get_heuristics_summary
from app.services.case_service import seed_presentation_cases, get_case_detail, generate_report
from app.models.models import Case, Alert, User, RoleEnum
from app.schemas.schemas import AlertDetailResponse


def test_graph_prefix_normalization():
    # Redundant / double prefix normalization
    assert normalize_entity_key("WALLET", "WALLET:1aSn...") == ("WALLET", "1aSn...", "WALLET:1aSn...")
    assert normalize_entity_key("TRANSACTION", "TX:12345") == ("TRANSACTION", "12345", "TRANSACTION:12345")
    assert normalize_entity_key("IP", "IP:10.0.0.1") == ("IP", "10.0.0.1", "IP:10.0.0.1")
    assert normalize_entity_key("UNKNOWN", "TX:abcdef") == ("TRANSACTION", "abcdef", "TRANSACTION:abcdef")


def test_alert_detail_schema_list_signals():
    # Verifies AlertDetailResponse accepts list of dicts contributing_signals
    raw_payload = {
        "id": 101,
        "entity_type": "WALLET",
        "entity_id": "bc1qtest123",
        "priority": "CRITICAL",
        "anomaly_score": 92.5,
        "risk_level": "CRITICAL",
        "status": "NEW",
        "review_state": "PENDING",
        "model_version": "v1.0",
        "contributing_signals": [
            {"signal": "FAN_OUT", "score": 0.88},
            {"signal": "BURST", "score": 0.94}
        ],
        "evidence_ids": [1, 2, 3],
        "created_at": None,
        "reviewed_at": None
    }
    validated = AlertDetailResponse(**raw_payload)
    assert validated.id == 101
    assert len(validated.contributing_signals) == 2
    assert validated.evidence_ids == [1, 2, 3]


def test_heuristics_summary_not_empty(db_session):
    summary = get_heuristics_summary(db_session)
    assert isinstance(summary, dict)
    assert "peeling_chains_detected" in summary
    assert "mixing_transactions_detected" in summary


def test_case_seeding_and_reporting(db_session):
    # Ensure at least one alert exists for seeding
    user = db_session.query(User).filter(User.username == "admin").first()
    if not user:
        user = User(username="admin", email="admin@test.com", hashed_password="pw", role=RoleEnum.ADMINISTRATOR)
        db_session.add(user)
        db_session.commit()

    alert = db_session.query(Alert).first()
    if not alert:
        alert = Alert(
            entity_type="WALLET",
            entity_id="bc1qseedtestwallet",
            priority="CRITICAL",
            anomaly_score=95.0,
            status="NEW"
        )
        db_session.add(alert)
        db_session.commit()

    seed_presentation_cases(db_session)
    cases = db_session.query(Case).all()
    assert len(cases) > 0

    first_case = cases[0]
    detail = get_case_detail(db_session, first_case.id)
    assert detail is not None
    assert detail["title"] is not None

    report = generate_report(db_session, first_case.id)
    assert report is not None
    assert report["report_type"] == "INVESTIGATION_REPORT"
    assert "disclaimer" in report
