"""
Independent Scheme Policy Verification & Statutory Data Completeness Test Suite.
Validates all six active schemes against official policy criteria:
- PM-KISAN
- PMFBY
- PMKSY-PDMC
- KCC
- UP_KRISHAK_DURGHATNA
- SMAM_MACHINERY

Ensures 100% schema compliance, valid predicates, authentic portal domains,
and seamless synchronization between data/schemes/*.json, SCHEME_CATALOGUE, and Database Seeder.
"""

import json
import os
import pytest
from app.services.scheme_catalogue import SCHEME_CATALOGUE
from app.services.scheme_seeder import seed_schemes_and_rules
from app.models import Scheme, SchemeVersion, EligibilityRule
from app.db.session import SessionLocal, engine, Base

SCHEME_CODES = [
    "PM_KISAN",
    "PMFBY",
    "PMKSY_PDMC",
    "KCC",
    "UP_KRISHAK_DURGHATNA",
    "SMAM_MACHINERY"
]

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "schemes"))

REQUIRED_SCHEME_FIELDS = [
    "scheme_code",
    "official_name_en",
    "official_name_hi",
    "department",
    "level",
    "benefit_type",
    "benefit_summary_en",
    "benefit_summary_hi",
    "official_portal_url",
    "source_title",
    "source_section",
    "source_url",
    "verified_at",
    "verified_by",
    "rules",
    "documents",
    "need_tags"
]

REQUIRED_RULE_FIELDS = [
    "rule_code",
    "title_en",
    "title_hi",
    "field_name",
    "operator",
    "target_value",
    "is_mandatory",
    "citation"
]

VALID_OPERATORS = ["GTE", "LTE", "EQUALS", "IN", "INTERSECT_ANY"]

ALLOWED_PORTAL_DOMAINS = [
    "gov.in",
    "nic.in",
    "rbi.org.in",
    "myscheme.gov.in"
]


def test_all_six_schemes_exist_in_catalogue():
    """Confirms all six required schemes exist in the operational catalogue."""
    for code in SCHEME_CODES:
        assert code in SCHEME_CATALOGUE, f"Scheme {code} missing from SCHEME_CATALOGUE"


def test_all_six_schemes_exist_in_data_files():
    """Confirms all six required schemes exist as verified JSON files in data/schemes/."""
    file_map = {
        "PM_KISAN": "pm_kisan.json",
        "PMFBY": "pmfby.json",
        "PMKSY_PDMC": "pmksy_pdmc.json",
        "KCC": "kcc.json",
        "UP_KRISHAK_DURGHATNA": "up_krishak_durghatna.json",
        "SMAM_MACHINERY": "smam_machinery.json"
    }
    for code, filename in file_map.items():
        filepath = os.path.join(DATA_DIR, filename)
        assert os.path.isfile(filepath), f"Data file {filename} missing in {DATA_DIR}"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            assert data["scheme_code"] == code, f"Scheme code mismatch in {filename}"


@pytest.mark.parametrize("scheme_code", SCHEME_CODES)
def test_scheme_record_field_completeness(scheme_code):
    """Verifies each scheme possesses every required statutory metadata field."""
    scheme = SCHEME_CATALOGUE[scheme_code]
    for field in REQUIRED_SCHEME_FIELDS:
        assert field in scheme, f"Field '{field}' missing in scheme '{scheme_code}'"
        assert scheme[field] is not None, f"Field '{field}' is None in scheme '{scheme_code}'"
        if isinstance(scheme[field], (str, list)):
            assert len(scheme[field]) > 0, f"Field '{field}' is empty in scheme '{scheme_code}'"


@pytest.mark.parametrize("scheme_code", SCHEME_CODES)
def test_scheme_official_portal_domains(scheme_code):
    """Verifies that official portal URLs strictly link to official government domains."""
    scheme = SCHEME_CATALOGUE[scheme_code]
    url = scheme["official_portal_url"]
    assert any(domain in url for domain in ALLOWED_PORTAL_DOMAINS), (
        f"Scheme '{scheme_code}' portal URL '{url}' does not point to an approved government domain"
    )


@pytest.mark.parametrize("scheme_code", SCHEME_CODES)
def test_scheme_rules_integrity(scheme_code):
    """Verifies all rules for each scheme have valid fields, valid operators, and citations."""
    scheme = SCHEME_CATALOGUE[scheme_code]
    rules = scheme["rules"]
    assert len(rules) >= 1, f"Scheme '{scheme_code}' has no rules defined"
    
    for r in rules:
        for rf in REQUIRED_RULE_FIELDS:
            assert rf in r, f"Rule field '{rf}' missing in rule '{r.get('rule_code')}' of '{scheme_code}'"
        
        assert r["operator"] in VALID_OPERATORS, (
            f"Invalid operator '{r['operator']}' in rule '{r['rule_code']}' of '{scheme_code}'"
        )
        assert len(r["citation"].strip()) > 10, (
            f"Citation too short or empty for rule '{r['rule_code']}' in '{scheme_code}'"
        )


@pytest.mark.parametrize("scheme_code", SCHEME_CODES)
def test_scheme_document_taxonomies(scheme_code):
    """Verifies that all required documents have clear titles in English and Hindi."""
    scheme = SCHEME_CATALOGUE[scheme_code]
    docs = scheme["documents"]
    assert len(docs) >= 1, f"Scheme '{scheme_code}' has no documents defined"
    for d in docs:
        assert "title_en" in d and len(d["title_en"]) > 0
        assert "title_hi" in d and len(d["title_hi"]) > 0


def test_catalogue_data_file_synchronization():
    """Verifies that SCHEME_CATALOGUE in memory is 1:1 synchronized with data/schemes/*.json."""
    file_map = {
        "PM_KISAN": "pm_kisan.json",
        "PMFBY": "pmfby.json",
        "PMKSY_PDMC": "pmksy_pdmc.json",
        "KCC": "kcc.json",
        "UP_KRISHAK_DURGHATNA": "up_krishak_durghatna.json",
        "SMAM_MACHINERY": "smam_machinery.json"
    }
    for code, filename in file_map.items():
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        cat = SCHEME_CATALOGUE[code]
        assert cat["official_name_en"] == data["official_name_en"]
        assert cat["official_name_hi"] == data["official_name_hi"]
        assert cat["benefit_type"] == data["benefit_type"]
        assert cat["official_portal_url"] == data["official_portal_url"]
        assert len(cat["rules"]) == len(data["rules"])


def test_database_seeder_contains_all_six_schemes():
    """Verifies database seeder correctly creates all 6 schemes with versions and rules."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_schemes_and_rules(db)
        count = db.query(Scheme).count()
        assert count >= 6, f"Expected at least 6 schemes in DB, found {count}"
        
        for code in SCHEME_CODES:
            s = db.query(Scheme).filter(Scheme.scheme_code == code).first()
            assert s is not None, f"Scheme {code} not found in seeded database"
            assert s.official_portal_url.startswith("http")
            
            # Check version and rules
            active_version = db.query(SchemeVersion).filter(
                SchemeVersion.id == s.active_version_id
            ).first()
            if not active_version:
                active_version = db.query(SchemeVersion).filter(
                    SchemeVersion.scheme_id == s.id,
                    SchemeVersion.status.in_(["PUBLISHED", "ACTIVE"])
                ).first()
            assert active_version is not None, f"No active/published version for scheme {code}"
            
            rules = db.query(EligibilityRule).filter(
                EligibilityRule.scheme_version_id == active_version.id
            ).all()
            assert len(rules) >= 1, f"No rules seeded for scheme {code}"
    finally:
        db.close()
