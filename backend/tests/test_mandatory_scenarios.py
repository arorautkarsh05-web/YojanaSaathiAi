import pytest
from app.services.eligibility_engine import (
    evaluate_scheme, evaluate_all_schemes, evaluate_single_rule, parse_landholding_to_acres
)
from app.services.geo_applicability import evaluate_geographic_applicability, normalize_district_name
from app.services.convergence_engine import find_pairwise_evidence, check_multi_scheme_convergence
from app.services.action_plan_service import generate_action_plan
from app.services.policy_impact_service import assess_policy_change_impact
from app.models import User, ActionPlan, AuditLog

# 1. New Farmer Onboarding & 2. Incomplete Profile
def test_scenario_incomplete_profile_yields_unknown_not_pass():
    incomplete = {"state": "Uttar Pradesh", "district": "Varanasi"}
    ev = evaluate_scheme("PM_KISAN", incomplete)
    assert ev.overall_status == "NEEDS_MORE_INFO"
    assert len(ev.unknown_rules) > 0
    assert any(r.status == "UNKNOWN" for r in ev.unknown_rules)

# 3. Invalid District
def test_scenario_invalid_district_rejected():
    res = evaluate_geographic_applicability("Invalid_Non_Existent_District", "Uttar Pradesh", "PM_KISAN")
    assert res.is_valid_up_district is False
    assert res.applicability_status == "UNKNOWN_REQUIRES_VERIFICATION"
    assert any("not recognized" in n for n in res.notes)

# 4. Missing Landholding & 5. Invalid Landholding Values
def test_scenario_invalid_landholding_negative_returns_error():
    acres, err = parse_landholding_to_acres(-5.0)
    assert acres is None
    assert "cannot be negative" in err

def test_scenario_missing_landholding_returns_unknown():
    rule = {
        "rule_code": "R_LAND", "title_en": "Land", "title_hi": "भूमि",
        "field_name": "landholding_acres", "operator": "GTE", "target_value": 1.0,
        "is_mandatory": True, "citation": "Statutory rule"
    }
    outcome = evaluate_single_rule(rule, {})
    assert outcome.status == "UNKNOWN"

# 6. PASS Eligibility
def test_scenario_pass_eligibility():
    profile = {
        "state": "Uttar Pradesh", "district": "Varanasi",
        "landholding_acres": 2.5, "is_institutional": False
    }
    ev = evaluate_scheme("PM_KISAN", profile)
    assert ev.overall_status == "LIKELY_ELIGIBLE"
    assert len(ev.passed_rules) >= 2
    assert len(ev.failed_rules) == 0

# 7. FAIL Eligibility
def test_scenario_fail_eligibility():
    profile = {
        "state": "Uttar Pradesh", "district": "Varanasi",
        "landholding_acres": 2.5, "is_institutional": True # Institutional landholder
    }
    ev = evaluate_scheme("PM_KISAN", profile)
    assert ev.overall_status == "LIKELY_NOT_ELIGIBLE"
    assert any(r.rule_code == "RULE_PMK_EXCLUSION_INSTITUTIONAL" and r.status == "FAIL" for r in ev.failed_rules)

# 8. UNKNOWN Eligibility
def test_scenario_unknown_eligibility():
    profile = {
        "state": "Uttar Pradesh", "district": "Jhansi",
        "landholding_acres": 2.0, "is_institutional": None # Missing institutional status
    }
    ev = evaluate_scheme("PM_KISAN", profile)
    assert ev.overall_status == "NEEDS_MORE_INFO"
    assert any(r.status == "UNKNOWN" for r in ev.unknown_rules)

# 9. Missing Documents
def test_scenario_missing_documents_tracked_in_checklist():
    plan = generate_action_plan(
        profile_data={"state": "Uttar Pradesh", "district": "Varanasi", "landholding_acres": 2.0},
        selected_scheme_codes=["PM_KISAN", "KCC"]
    )
    assert len(plan.checklist_items) >= 2
    # Ensure all items default to is_ready = False
    assert all(item.is_ready is False for item in plan.checklist_items)
    # Check shared document deduplication
    aadhaar_item = next((item for item in plan.checklist_items if "aadhaar" in item.id.lower() or "identity" in item.id.lower()), None)
    if aadhaar_item:
        assert len(aadhaar_item.required_for_schemes) >= 1

# 10. Independent Pairwise Convergence
def test_scenario_convergence_pairwise_independence():
    pairs = check_multi_scheme_convergence(["PM_KISAN", "KCC", "PMFBY"])
    assert len(pairs) == 3
    # No transitivity inferred
    for p in pairs:
        assert p.status in ["COMPATIBLE_CONFIRMED", "INCOMPATIBLE_CONFIRMED", "UNKNOWN_REQUIRES_VERIFICATION"]

# 11. Unverified Pair Returns UNKNOWN_REQUIRES_VERIFICATION
def test_scenario_unverified_scheme_compatibility():
    pair = find_pairwise_evidence("PMFBY", "SMAM_MACHINERY")
    assert pair.status == "UNKNOWN_REQUIRES_VERIFICATION"
    assert "Pending Inter-Departmental Review" in pair.authoritative_source

from app.db.session import SessionLocal

# 12. Policy Impact Assessment on Saved Action Plans
def test_scenario_policy_impact_assessment():
    db = SessionLocal()
    try:
        impact = assess_policy_change_impact(
            db=db,
            scheme_code="PM_KISAN",
            new_version_tag="2026.1_AMENDED",
            amendment_summary="Mandatory biometric e-KYC deadline extended by State Nodal Agency."
        )
        assert impact["status"] == "IMPACT_EVALUATED"
        assert impact["scheme_code"] == "PM_KISAN"
        assert "affected_plans_count" in impact
    finally:
        db.close()

# 13. Prompt-Aligned SchemeEvaluation Schema Properties
def test_scenario_scheme_evaluation_contract_compliance():
    profile = {
        "state": "Uttar Pradesh", "district": "Barabanki",
        "landholding_acres": 1.5, "is_institutional": False
    }
    ev = evaluate_scheme("PM_KISAN", profile)
    # Verify exact prompt-specified properties
    assert hasattr(ev, "scheme_id")
    assert hasattr(ev, "overall_status")
    assert hasattr(ev, "conditions")
    assert hasattr(ev, "passed_conditions")
    assert hasattr(ev, "failed_conditions")
    assert hasattr(ev, "unknown_conditions")
    assert hasattr(ev, "missing_information")
    assert hasattr(ev, "policy_version")
    assert hasattr(ev, "evidence_references")
    assert hasattr(ev, "assessment_timestamp")
    assert hasattr(ev, "disclaimer")
    assert ev.disclaimer is not None
