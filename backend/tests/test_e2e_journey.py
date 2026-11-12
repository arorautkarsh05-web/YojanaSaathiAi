import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_complete_guest_farmer_journey():
    """
    Validates PRD Section 16.5 End-to-End Acceptance:
    1. Enter as guest (no registration).
    2. Enter stated needs (irrigation, income support).
    3. Confirm farm profile (District: Varanasi, Land: 1.5 acres, Crops: wheat/paddy, Irrigation: tubeWell).
    4. Deterministic rules evaluate schemes.
    5. Check multi-scheme convergence for PM_KISAN + PMKSY_PDMC.
    6. Generate Farmer Benefit Action Plan.
    7. Verify document readiness checklist and official next steps are returned.
    """
    # Step 1 & 2 & 3: Stated Needs & Profile Evaluation
    rec_resp = client.post("/api/v1/recommendations", json={
        "stated_needs": ["income_support", "irrigation"],
        "profile": {
            "district": "Varanasi",
            "landholding_acres": 1.5,
            "farmer_category": "MARGINAL",
            "primary_crops": ["wheat", "paddy"],
            "irrigation_source": "tubeWell",
            "social_category": "OBC",
            "is_temporary": True
        }
    })
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert rec_data["total_schemes_evaluated"] == 6
    schemes = rec_data["schemes"]

    # Verify PM-KISAN evaluation
    pmk = next(s for s in schemes if s["scheme_code"] == "PM_KISAN")
    assert pmk["overall_status"] in ["LIKELY_ELIGIBLE", "NEEDS_MORE_INFO"]
    assert pmk["official_portal_url"] == "https://pmkisan.gov.in"
    assert len(pmk["passed_rules"]) > 0

    # Step 4: Multi-Scheme Convergence Check
    conv_resp = client.post("/api/v1/convergence/check", json={
        "scheme_codes": ["PM_KISAN", "PMFBY"]
    })
    assert conv_resp.status_code == 200
    conv_data = conv_resp.json()
    assert len(conv_data["pairs"]) == 1
    assert conv_data["pairs"][0]["status"] == "COMPATIBLE_CONFIRMED"

    # Step 5: Generate Action Plan
    plan_resp = client.post("/api/v1/action-plans", json={
        "selected_scheme_codes": ["PM_KISAN", "PMKSY_PDMC"],
        "profile": {
            "district": "Varanasi",
            "landholding_acres": 1.5,
            "farmer_category": "MARGINAL",
            "primary_crops": ["wheat", "paddy"],
            "irrigation_source": "tubeWell",
            "social_category": "OBC",
            "is_temporary": True
        },
        "checklist_states": {"doc_khatauni": True}
    })
    assert plan_resp.status_code == 200
    plan_data = plan_resp.json()
    assert "YS-UP-" in plan_data["plan_number"]
    assert len(plan_data["selected_schemes"]) == 2
    assert len(plan_data["checklist_items"]) >= 2
    assert len(plan_data["official_steps"]) >= 2
    assert "योजना साथी" in plan_data["disclaimer"]

def test_grounded_qa_safeguard():
    # Grounded question about PM-KISAN amount
    resp1 = client.post("/api/v1/assistant/query", json={
        "query": "पीएम-किसान में कितना लाभ मिलता है?",
        "scheme_code": "PM_KISAN"
    })
    assert resp1.status_code == 200
    data1 = resp1.json()
    assert data1["can_verify"] is True
    assert "₹6,000" in data1["answer"]

    # Unverified question outside statutory gazette records
    resp2 = client.post("/api/v1/assistant/query", json={
        "query": "कल मौसम कैसा रहेगा?",
    })
    assert resp2.status_code == 200
    data2 = resp2.json()
    assert data2["can_verify"] is False
    assert "सत्यापित सरकारी नियमों में दर्ज नहीं है" in data2["answer"]

