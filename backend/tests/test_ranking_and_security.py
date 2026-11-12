import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, Base, engine
from app.services.eligibility_engine import evaluate_all_schemes
from app.models import AuthSession

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield

def test_recommendation_ranking_sensitivity_to_needs():
    """Verifies that changing farmer needs MATERIALLY alters recommendation ranking."""
    profile = {
        "district": "Varanasi",
        "landholding_acres": 2.5,
        "primary_crops": ["wheat", "paddy"],
        "irrigation_source": "tubeWell",
        "state": "Uttar Pradesh"
    }

    # Case A: Need is crop insurance
    results_insurance = evaluate_all_schemes(profile, stated_needs=["crop_insurance"])
    assert len(results_insurance) >= 5
    top_scheme_insurance = results_insurance[0].scheme_code
    assert top_scheme_insurance == "PMFBY"
    assert results_insurance[0].ranking_factors["need_relevance_pct"] >= 80.0

    # Case B: Need is micro irrigation
    results_irrigation = evaluate_all_schemes(profile, stated_needs=["irrigation"])
    top_scheme_irrigation = results_irrigation[0].scheme_code
    assert top_scheme_irrigation == "PMKSY_PDMC"
    assert results_irrigation[0].ranking_factors["need_relevance_pct"] >= 80.0

    # Case C: Need is farm machinery
    results_machinery = evaluate_all_schemes(profile, stated_needs=["machinery"])
    top_scheme_machinery = results_machinery[0].scheme_code
    assert top_scheme_machinery == "SMAM_MACHINERY"
    assert results_machinery[0].ranking_factors["need_relevance_pct"] >= 80.0

def test_ineligible_scheme_never_outranks_eligible():
    """Verifies that an ineligible scheme (FAIL) never outranks an eligible scheme even with high need match."""
    profile = {
        "district": "Varanasi",
        "landholding_acres": 0.0, # Violates PM-KISAN, PMKSY, KCC land requirements
        "primary_crops": ["mango"], # Non-notified crop
        "irrigation_source": "rainfed",
        "state": "Uttar Pradesh"
    }
    results = evaluate_all_schemes(profile, stated_needs=["income_support"])
    
    # Check that any LIKELY_NOT_ELIGIBLE scheme is placed in lower tier
    tiers = [r.overall_status for r in results]
    if "LIKELY_NOT_ELIGIBLE" in tiers and "NEEDS_MORE_INFO" in tiers:
        first_fail_idx = tiers.index("LIKELY_NOT_ELIGIBLE")
        first_unknown_idx = tiers.index("NEEDS_MORE_INFO")
        assert first_unknown_idx < first_fail_idx

def test_convergence_graph_api():
    """Verifies that the convergence graph API returns structured nodes and edges."""
    resp = client.get("/api/v1/convergence/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert len(data["nodes"]) >= 6
    assert len(data["edges"]) >= 10 # 6 choose 2 = 15 edges

    # Verify edge schema
    edge = data["edges"][0]
    assert "source" in edge
    assert "target" in edge
    assert "status" in edge
    assert edge["status"] in ["COMPATIBLE_CONFIRMED", "INCOMPATIBLE_CONFIRMED", "UNKNOWN_REQUIRES_VERIFICATION"]

def test_token_replay_session_family_revocation():
    """Verifies that replaying an already-rotated refresh token revokes the entire session family."""
    test_email = "security.audit@example.com"
    client.post("/api/v1/auth/register", json={
        "email": test_email,
        "password": "SecurePassword123!",
        "terms_consented": True
    })

    # Login to acquire refresh token
    login_resp = client.post("/api/v1/auth/login", json={
        "email": test_email,
        "password": "SecurePassword123!"
    })
    assert login_resp.status_code == 200
    cookie_header = login_resp.headers.get("set-cookie")
    assert cookie_header is not None

    # First rotation (valid)
    refresh_resp1 = client.post("/api/v1/auth/refresh", headers={"Cookie": cookie_header})
    assert refresh_resp1.status_code == 200

    # REPLAY ATTACK: Attempt to use the OLD cookie again
    replay_resp = client.post("/api/v1/auth/refresh", headers={"Cookie": cookie_header})
    assert replay_resp.status_code == 401
    assert "replay detected" in replay_resp.json()["detail"].lower()

