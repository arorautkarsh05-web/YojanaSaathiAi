"""
Tests for Geographic Applicability, Boundary Conditions, Readiness Engine, and Privacy APIs.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, Base, engine
from app.services.geo_applicability import evaluate_geographic_applicability, normalize_district_name
from app.services.eligibility_engine import evaluate_all_schemes, parse_landholding_to_acres
from app.services.readiness_engine import evaluate_farmer_scheme_readiness

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_liveness_and_readiness_probes():
    """Verifies that /live and /ready endpoints function and verify database."""
    live_resp = client.get("/live")
    assert live_resp.status_code == 200
    assert live_resp.json()["status"] == "alive"

    ready_resp = client.get("/ready")
    assert ready_resp.status_code == 200
    assert ready_resp.json()["status"] == "ready"
    assert ready_resp.json()["database"] == "connected"

def test_district_normalization_and_zones():
    """Verifies district alias normalization and agro-climatic zoning."""
    assert normalize_district_name("varanasi") == "Varanasi"
    assert normalize_district_name("Allahabad") == "Prayagraj"
    assert normalize_district_name("Faizabad") == "Ayodhya"
    assert normalize_district_name("lakhimpur") == "Kheri (Lakhimpur)"
    assert normalize_district_name("InvalidCityXYZ") is None

def test_geographic_applicability_out_of_state():
    """Verifies that an out-of-state request receives NOT_APPLICABLE and zero geo score."""
    res = evaluate_geographic_applicability(district="Patna", state="Bihar", scheme_code="PM_KISAN")
    assert res.is_valid_up_district is False
    assert res.applicability_status == "NOT_APPLICABLE"
    assert res.geo_score == 0.0

def test_geographic_applicability_critical_water_zone():
    """Verifies that a critical groundwater district receives priority for PMKSY-PDMC."""
    res = evaluate_geographic_applicability(district="Agra", state="Uttar Pradesh", scheme_code="PMKSY_PDMC")
    assert res.is_valid_up_district is True
    assert res.is_critical_water_zone is True
    assert res.applicability_status == "APPLICABLE_WITH_PRIORITY"
    assert res.geo_score == 100.0

def test_negative_landholding_returns_unknown():
    """Verifies that negative landholding is treated as invalid input returning UNKNOWN, not FAIL."""
    profile = {
        "district": "Varanasi",
        "landholding_acres": -2.5,
        "primary_crops": ["wheat", "paddy"],
        "state": "Uttar Pradesh"
    }
    results = evaluate_all_schemes(profile, stated_needs=["income_support"])
    pm_kisan = next(r for r in results if r.scheme_code == "PM_KISAN")
    
    # Assert land rule returned UNKNOWN due to negative physical value
    land_rule = next(r for r in pm_kisan.unknown_rules if r.rule_code == "RULE_PMK_LAND")
    assert land_rule.status == "UNKNOWN"
    assert "cannot be negative" in land_rule.reason

def test_bigha_unit_conversion():
    """Verifies that UP pucca bigha is correctly converted to acres (4 bigha = 2.5 acres)."""
    acres, err = parse_landholding_to_acres("4 bigha")
    assert err is None
    assert acres == 2.5

    acres_hint, err_hint = parse_landholding_to_acres("4", unit_hint="bigha")
    assert err_hint is None
    assert acres_hint == 2.5

def test_readiness_engine_states():
    """Verifies that the readiness engine computes correct states and transparent scores."""
    # Case A: Fully ready
    res_ready = evaluate_farmer_scheme_readiness(
        scheme_code="PM_KISAN",
        overall_status="LIKELY_ELIGIBLE",
        unknown_rule_count=0,
        failed_rule_count=0,
        total_docs_count=3,
        ready_docs_count=3,
        geo_applicability="APPLICABLE",
        verification_status="VERIFIED"
    )
    assert res_ready.readiness_state == "READY_FOR_OFFICIAL_APPLICATION_REVIEW"
    assert res_ready.readiness_score_pct == 100.0

    # Case B: Documents pending
    res_docs = evaluate_farmer_scheme_readiness(
        scheme_code="PM_KISAN",
        overall_status="LIKELY_ELIGIBLE",
        unknown_rule_count=0,
        failed_rule_count=0,
        total_docs_count=3,
        ready_docs_count=1,
        geo_applicability="APPLICABLE",
        verification_status="VERIFIED"
    )
    assert res_docs.readiness_state == "DOCUMENTS_PENDING"
    assert res_docs.readiness_score_pct < 100.0

def test_dpdp_privacy_endpoints():
    """Verifies consent withdrawal, data export, and account deletion endpoints."""
    test_email = "dpdp.farmer@example.com"
    reg_resp = client.post("/api/v1/auth/register", json={
        "email": test_email,
        "password": "SecurePassword123!",
        "terms_consented": True
    })
    assert reg_resp.status_code in [201, 400]

    login_resp = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "SecurePassword123!"
    })
    assert login_resp.status_code == 200
    token = login_resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Export Data
    export_resp = client.get("/api/v1/auth/export-data", headers=headers)
    assert export_resp.status_code == 200
    data = export_resp.json()
    assert data["user_account"]["email"] == test_email
    assert "data_fiduciary" in data["export_metadata"]

    # 2. Withdraw Consent
    withdraw_resp = client.post("/api/v1/auth/consent/withdraw", headers=headers)
    assert withdraw_resp.status_code == 200
    assert withdraw_resp.json()["status"] == "REVOKED"

    # 3. Delete Account (Right to Erasure)
    delete_resp = client.delete("/api/v1/auth/delete-account", headers=headers)
    assert delete_resp.status_code == 200
    assert delete_resp.json()["status"] == "PURGED"

    # Verify user can no longer log in
    relogin_resp = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "SecurePassword123!"
    })
    assert relogin_resp.status_code == 401
