import pytest
from app.services.convergence_engine import find_pairwise_evidence, check_multi_scheme_convergence
from app.services.scheme_catalogue import SCHEME_CATALOGUE

ACTIVE_6_SCHEMES = [
    "PM_KISAN",
    "PMFBY",
    "PMKSY_PDMC",
    "KCC",
    "UP_KRISHAK_DURGHATNA",
    "SMAM_MACHINERY"
]

def test_exact_15_pairwise_combinations_count():
    """Confirms that 6 active schemes produce exactly 15 pairwise combinations."""
    pairs = check_multi_scheme_convergence(ACTIVE_6_SCHEMES)
    assert len(pairs) == 15, f"Expected exactly 15 pairs for 6 schemes, got {len(pairs)}"

@pytest.mark.parametrize("scheme_a,scheme_b,expected_status", [
    ("PM_KISAN", "KCC", "COMPATIBLE_CONFIRMED"),
    ("PM_KISAN", "PMFBY", "COMPATIBLE_CONFIRMED"),
    ("PM_KISAN", "PMKSY_PDMC", "COMPATIBLE_CONFIRMED"),
    ("PM_KISAN", "UP_KRISHAK_DURGHATNA", "COMPATIBLE_CONFIRMED"),
    ("PM_KISAN", "SMAM_MACHINERY", "COMPATIBLE_CONFIRMED"),
    ("PMFBY", "KCC", "COMPATIBLE_CONFIRMED"),
    ("PMFBY", "PMKSY_PDMC", "COMPATIBLE_CONFIRMED"),
    ("PMFBY", "UP_KRISHAK_DURGHATNA", "COMPATIBLE_CONFIRMED"),
    ("PMFBY", "SMAM_MACHINERY", "UNKNOWN_REQUIRES_VERIFICATION"),
    ("PMKSY_PDMC", "KCC", "COMPATIBLE_CONFIRMED"),
    ("PMKSY_PDMC", "SMAM_MACHINERY", "COMPATIBLE_CONFIRMED"),
    ("PMKSY_PDMC", "UP_KRISHAK_DURGHATNA", "COMPATIBLE_CONFIRMED"),
    ("KCC", "SMAM_MACHINERY", "COMPATIBLE_CONFIRMED"),
    ("KCC", "UP_KRISHAK_DURGHATNA", "COMPATIBLE_CONFIRMED"),
    ("UP_KRISHAK_DURGHATNA", "SMAM_MACHINERY", "COMPATIBLE_CONFIRMED"),
])
def test_all_15_individual_convergence_pairs(scheme_a, scheme_b, expected_status):
    """Verifies that each of the 15 pairs returns its verified statutory status and evidence."""
    # Test (A, B)
    pair_ab = find_pairwise_evidence(scheme_a, scheme_b)
    assert pair_ab.status == expected_status
    assert len(pair_ab.evidence_text) > 20
    assert len(pair_ab.authoritative_source) > 5

    # Test bidirectional symmetry (B, A)
    pair_ba = find_pairwise_evidence(scheme_b, scheme_a)
    assert pair_ba.status == expected_status

def test_anti_transitivity_guarantee():
    """
    Verifies anti-transitivity:
    Even though PM_KISAN is compatible with PMFBY, and PM_KISAN is compatible with SMAM_MACHINERY,
    PMFBY + SMAM_MACHINERY remains strictly UNKNOWN_REQUIRES_VERIFICATION.
    """
    pair_kisan_pmfby = find_pairwise_evidence("PM_KISAN", "PMFBY")
    pair_kisan_smam = find_pairwise_evidence("PM_KISAN", "SMAM_MACHINERY")
    pair_pmfby_smam = find_pairwise_evidence("PMFBY", "SMAM_MACHINERY")

    assert pair_kisan_pmfby.status == "COMPATIBLE_CONFIRMED"
    assert pair_kisan_smam.status == "COMPATIBLE_CONFIRMED"
    # Transitivity must NOT be inferred!
    assert pair_pmfby_smam.status == "UNKNOWN_REQUIRES_VERIFICATION"
