import pytest
from app.services.eligibility_engine import evaluate_single_rule, evaluate_scheme, evaluate_all_schemes
from app.services.scheme_catalogue import SCHEME_CATALOGUE

def test_pmkisan_rule_pass():
    rule = {
        "rule_code": "RULE_PMK_LAND",
        "title_en": "Cultivable Land Record",
        "title_hi": "कृषि भूमि",
        "field_name": "landholding_acres",
        "operator": "GTE",
        "target_value": 0.01,
        "is_mandatory": True,
        "citation": "PM-KISAN Guidelines Sec 2"
    }
    profile = {"landholding_acres": 2.5}
    outcome = evaluate_single_rule(rule, profile)
    assert outcome.status == "PASS"

def test_pmkisan_rule_fail():
    rule = {
        "rule_code": "RULE_PMK_LAND",
        "title_en": "Cultivable Land Record",
        "title_hi": "कृषि भूमि",
        "field_name": "landholding_acres",
        "operator": "GTE",
        "target_value": 0.01,
        "is_mandatory": True,
        "citation": "PM-KISAN Guidelines Sec 2"
    }
    profile = {"landholding_acres": 0.0}
    outcome = evaluate_single_rule(rule, profile)
    assert outcome.status == "FAIL"

def test_pmkisan_rule_unknown_when_data_missing():
    """Non-negotiable rule 2: Missing or ambiguous data must NEVER become PASS."""
    rule = {
        "rule_code": "RULE_PMK_LAND",
        "title_en": "Cultivable Land Record",
        "title_hi": "कृषि भूमि",
        "field_name": "landholding_acres",
        "operator": "GTE",
        "target_value": 0.01,
        "is_mandatory": True,
        "citation": "PM-KISAN Guidelines Sec 2"
    }
    # Profile completely missing landholding_acres
    profile = {"district": "Varanasi"}
    outcome = evaluate_single_rule(rule, profile)
    assert outcome.status == "UNKNOWN"

def test_pmfby_crop_intersection_pass():
    rule = {
        "rule_code": "RULE_PMFBY_NOTIFIED_CROP",
        "title_en": "Notified Crops",
        "title_hi": "अधिसूचित फसल",
        "field_name": "primary_crops",
        "operator": "INTERSECT_ANY",
        "target_value": ["wheat", "paddy", "sugarcane"],
        "is_mandatory": True,
        "citation": "PMFBY Sec 4"
    }
    profile = {"primary_crops": ["wheat", "mustard"]}
    outcome = evaluate_single_rule(rule, profile)
    assert outcome.status == "PASS"

def test_pmfby_crop_intersection_fail():
    rule = {
        "rule_code": "RULE_PMFBY_NOTIFIED_CROP",
        "title_en": "Notified Crops",
        "title_hi": "अधिसूचित फसल",
        "field_name": "primary_crops",
        "operator": "INTERSECT_ANY",
        "target_value": ["wheat", "paddy", "sugarcane"],
        "is_mandatory": True,
        "citation": "PMFBY Sec 4"
    }
    profile = {"primary_crops": ["coffee", "rubber"]}
    outcome = evaluate_single_rule(rule, profile)
    assert outcome.status == "FAIL"

def test_scheme_overall_status_likely_eligible():
    profile = {
        "district": "Gorakhpur",
        "state": "Uttar Pradesh",
        "landholding_acres": 1.8,
        "is_institutional": "false"
    }
    eval_res = evaluate_scheme("PM_KISAN", profile)
    assert eval_res.overall_status == "LIKELY_ELIGIBLE"
    assert len(eval_res.failed_rules) == 0

def test_scheme_overall_status_needs_more_info():
    # Missing is_institutional check
    profile = {
        "district": "Lucknow",
        "state": "Uttar Pradesh",
        "landholding_acres": 2.0
    }
    eval_res = evaluate_scheme("PM_KISAN", profile)
    assert eval_res.overall_status == "NEEDS_MORE_INFO"
    assert len(eval_res.unknown_rules) > 0

def test_scheme_overall_status_likely_not_eligible():
    profile = {
        "district": "Agra",
        "state": "Uttar Pradesh",
        "landholding_acres": 0.0, # Zero land
        "is_institutional": "false"
    }
    eval_res = evaluate_scheme("PM_KISAN", profile)
    assert eval_res.overall_status == "LIKELY_NOT_ELIGIBLE"

