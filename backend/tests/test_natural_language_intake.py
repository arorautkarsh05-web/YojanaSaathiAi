import pytest
from app.services.farmer_intake_service import parse_conversational_intake
from app.schemas import ConversationalIntakeRequest
from app.services.eligibility_engine import evaluate_all_schemes

def test_hindi_conversational_intake_with_prompt_example():
    """
    Tests Phase 7 exact specification:
    'मेरे पास दो बीघा जमीन है और मैं गेहूं की खेती करता हूं। मुझे सिंचाई के लिए सरकारी सहायता चाहिए।'
    """
    req = ConversationalIntakeRequest(
        text="मेरे पास दो बीघा जमीन है और मैं गेहूं की खेती करता हूं। मुझे सिंचाई के लिए सरकारी सहायता चाहिए।",
        preferred_language="hi"
    )
    res = parse_conversational_intake(req)

    assert res.detected_language == "hi"
    assert res.intent == "irrigation_subsidy"
    assert "wheat" in res.extracted_parameters.crops
    assert res.extracted_parameters.land_unit == "bigha"
    assert res.extracted_parameters.landholding_acres == 1.25

    # Mandatory rule: Flag Bigha ambiguity and prompt farmer to confirm Pucca vs Kachha Bigha
    assert len(res.ambiguities) == 1
    assert res.ambiguities[0].issue == "LOCAL_UNIT_VARIATION"
    assert "पक्का बीघा" in res.ambiguities[0].clarification_prompt_hi
    assert "कच्चा बीघा" in res.ambiguities[0].clarification_prompt_hi

    # Missing district check
    assert "district" in res.missing_information
    assert any("जिले" in q for q in res.follow_up_questions_hi)
    assert res.can_proceed_to_evaluation is False

def test_intake_with_complete_attributes_enables_evaluation():
    """
    When farmer specifies district and landholding, structured profile is generated
    and directly evaluable by the deterministic rules engine.
    """
    req = ConversationalIntakeRequest(
        text="मैं झांसी से हूं, 2 एकड़ जमीन है और गेहूं व चना उगाता हूं। मुझे केसीसी लोन चाहिए।",
        preferred_language="hi"
    )
    res = parse_conversational_intake(req)

    assert res.extracted_parameters.district == "Jhansi"
    assert res.extracted_parameters.landholding_acres == 2.0
    assert "wheat" in res.extracted_parameters.crops
    assert "pulses" in res.extracted_parameters.crops
    assert res.intent == "institutional_credit"
    assert res.can_proceed_to_evaluation is True
    assert res.structured_profile_candidate is not None
    assert res.structured_profile_candidate.district == "Jhansi"
    assert res.structured_profile_candidate.farmer_category == "MARGINAL"

    # Pipe directly into deterministic rules engine
    profile_dict = res.structured_profile_candidate.model_dump()
    evals = evaluate_all_schemes(profile_dict, stated_needs=res.extracted_parameters.stated_needs)
    assert len(evals) >= 5

    kcc_eval = next((e for e in evals if e.scheme_code == "KCC"), None)
    assert kcc_eval is not None
    assert kcc_eval.overall_status == "LIKELY_ELIGIBLE"

def test_hinglish_intake_detection():
    req = ConversationalIntakeRequest(
        text="Mera district Varanasi hai, 3 acre jamin hai, dhan aur gehu lagaya hai, fasal bima chahiye",
        preferred_language="hinglish"
    )
    res = parse_conversational_intake(req)
    assert res.extracted_parameters.district == "Varanasi"
    assert res.extracted_parameters.landholding_acres == 3.0
    assert "paddy" in res.extracted_parameters.crops
    assert "wheat" in res.extracted_parameters.crops
    assert res.intent == "crop_insurance"
    assert res.can_proceed_to_evaluation is True

def test_safe_offline_intake_fallback():
    """
    When input is obscure or completely non-agricultural, never crash.
    Return safe uncertainty and guide user.
    """
    req = ConversationalIntakeRequest(
        text="नमस्ते, मुझे सामान्य जानकारी चाहिए",
        preferred_language="hi"
    )
    res = parse_conversational_intake(req)
    assert res.detected_language == "hi"
    assert res.can_proceed_to_evaluation is False
    assert "district" in res.missing_information
    assert "landholding" in res.missing_information

