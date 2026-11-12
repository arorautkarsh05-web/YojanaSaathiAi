import pytest
from app.services.convergence_engine import find_pairwise_evidence, check_multi_scheme_convergence

def test_approved_pair_pmkisan_and_pmfby():
    pair = find_pairwise_evidence("PM_KISAN", "PMFBY")
    assert pair.status == "COMPATIBLE_CONFIRMED"
    assert "PM-KISAN operational guidelines" in pair.evidence_text
    assert pair.authoritative_source != ""

def test_approved_pair_pmkisan_and_kcc():
    pair = find_pairwise_evidence("PM_KISAN", "KCC")
    assert pair.status == "COMPATIBLE_CONFIRMED"

def test_unverified_pair_returns_unknown_requires_verification():
    """Non-negotiable rule 3: Scheme compatibility requires approved authoritative evidence; otherwise UNKNOWN_REQUIRES_VERIFICATION."""
    pair = find_pairwise_evidence("PMFBY", "SMAM_MACHINERY")
    assert pair.status == "UNKNOWN_REQUIRES_VERIFICATION"
    assert "Pending Inter-Departmental Review" in pair.authoritative_source

def test_multi_scheme_pairwise_results_are_independent():
    # 3 schemes: PM_KISAN, PMFBY, SMAM_MACHINERY
    pairs = check_multi_scheme_convergence(["PM_KISAN", "PMFBY", "SMAM_MACHINERY"])
    # 3 choose 2 = 3 pairs
    assert len(pairs) == 3
    
    statuses = {f"{p.scheme_code_a}_{p.scheme_code_b}": p.status for p in pairs}
    # PM_KISAN + PMFBY is COMPATIBLE_CONFIRMED
    assert statuses.get("PM_KISAN_PMFBY") == "COMPATIBLE_CONFIRMED"
    # PMFBY + SMAM_MACHINERY is UNKNOWN_REQUIRES_VERIFICATION
    assert statuses.get("PMFBY_SMAM_MACHINERY") == "UNKNOWN_REQUIRES_VERIFICATION"

