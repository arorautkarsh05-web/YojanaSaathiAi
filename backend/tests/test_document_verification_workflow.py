import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal, Base, engine
from app.models import (
    FarmerDocument, DocumentVerificationRecord, ActionItemCompletion,
    FarmerApplicationProgress, BenefitVerificationRecord, ActionPlanConfirmation,
    ActionPlan, FarmerProfile
)
from app.services.document_verification_service import (
    get_required_documents_for_schemes, validate_file_bytes
)

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def clean_db():
    db = SessionLocal()
    try:
        db.query(ActionPlanConfirmation).delete()
        db.query(BenefitVerificationRecord).delete()
        db.query(FarmerApplicationProgress).delete()
        db.query(ActionItemCompletion).delete()
        db.query(DocumentVerificationRecord).delete()
        db.query(FarmerDocument).delete()
        db.commit()
    finally:
        db.close()


def test_dynamic_document_deduplication():
    # Test deduplication across PM_KISAN and PMKSY
    specs = get_required_documents_for_schemes(["PM_KISAN", "PMKSY"])
    spec_keys = [s.doc_id_key for s in specs]

    # Shared documents should appear only once
    assert spec_keys.count("doc_khatauni") == 1
    assert spec_keys.count("doc_bank_passbook") == 1
    assert spec_keys.count("doc_aadhaar") == 1

    khatauni_spec = next(s for s in specs if s.doc_id_key == "doc_khatauni")
    assert "PM_KISAN" in khatauni_spec.applicable_schemes
    assert "PMKSY" in khatauni_spec.applicable_schemes


def test_magic_byte_mime_validation():
    # Valid PDF bytes
    pdf_bytes = b"%PDF-1.4 sample content"
    assert validate_file_bytes(pdf_bytes) == "application/pdf"

    # Valid JPEG bytes
    jpeg_bytes = b"\xFF\xD8\xFF\xE0\x00\x10JFIF sample"
    assert validate_file_bytes(jpeg_bytes) == "image/jpeg"

    # Valid PNG bytes
    png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
    assert validate_file_bytes(png_bytes) == "image/png"

    # Invalid fake file
    with pytest.raises(Exception):
        validate_file_bytes(b"<html><script>alert(1)</script></html>")

    # Empty file
    with pytest.raises(Exception):
        validate_file_bytes(b"")


def test_complete_action_plan_verification_workflow(client):
    # 1. Create an Action Plan
    plan_payload = {
        "profile": {
            "district": "Varanasi",
            "landholding_acres": 2.0,
            "farmer_category": "SMALL",
            "primary_crops": ["Wheat", "Paddy"],
            "social_category": "GENERAL",
            "irrigation_source": "TUBEWELL",
            "is_temporary": True
        },
        "selected_scheme_codes": ["PM_KISAN", "PMKSY"]
    }
    create_res = client.post("/api/v1/action-plans", json=plan_payload)
    assert create_res.status_code == 200
    plan_data = create_res.json()
    plan_number = plan_data["plan_number"]
    assert plan_number.startswith("YS-UP-")

    # 2. Check workflow status (Prerequisites initially unmet)
    wf_res = client.get(f"/api/v1/action-plans/{plan_number}/workflow")
    assert wf_res.status_code == 200
    wf_data = wf_res.json()
    assert wf_data["can_confirm"] is False
    assert len(wf_data["unmet_prerequisites"]) > 0

    # 3. Document verification via 1-click tick-box and file upload
    fake_pdf = b"%PDF-1.5 \n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"

    # A) Khatauni via 1-click tick-box toggle
    tick_res = client.post(
        f"/api/v1/action-plans/{plan_number}/documents/doc_khatauni/toggle",
        json={"doc_id_key": "doc_khatauni", "is_checked": True}
    )
    assert tick_res.status_code == 200
    khatauni_doc = tick_res.json()
    assert khatauni_doc["verification_status"] == "VERIFIED"

    # B) Bank Passbook via 1-click tick-box toggle
    tick_res2 = client.post(
        f"/api/v1/action-plans/{plan_number}/documents/doc_bank_passbook/toggle",
        json={"doc_id_key": "doc_bank_passbook", "is_checked": True}
    )
    assert tick_res2.status_code == 200
    bank_doc = tick_res2.json()
    assert bank_doc["verification_status"] == "VERIFIED"

    # C) Aadhaar Upload (Auto-verified on upload)
    upload_res3 = client.post(
        f"/api/v1/action-plans/{plan_number}/documents/upload",
        data={"doc_id_key": "doc_aadhaar"},
        files={"file": ("masked_aadhaar.pdf", io.BytesIO(fake_pdf), "application/pdf")}
    )
    assert upload_res3.status_code == 200
    aadhaar_doc = upload_res3.json()["document"]
    assert aadhaar_doc["verification_status"] == "VERIFIED"

    # D) Photo Upload (Auto-verified on upload)
    fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    upload_res4 = client.post(
        f"/api/v1/action-plans/{plan_number}/documents/upload",
        data={"doc_id_key": "doc_photo"},
        files={"file": ("photo.png", io.BytesIO(fake_png), "image/png")}
    )
    assert upload_res4.status_code == 200
    photo_doc = upload_res4.json()["document"]
    assert photo_doc["verification_status"] == "VERIFIED"

    # 4. Reviewer verification actions (Backend capability test)
    # Test rejection without reason fails
    reject_fail = client.post(
        f"/api/v1/action-plans/{plan_number}/documents/{khatauni_doc['id']}/verify",
        json={"action": "REJECT"}
    )
    assert reject_fail.status_code == 400

    # Ensure all 4 documents remain VERIFIED
    for doc in [khatauni_doc, bank_doc, aadhaar_doc, photo_doc]:
        app_res = client.post(
            f"/api/v1/action-plans/{plan_number}/documents/{doc['id']}/verify",
            json={"action": "APPROVE", "remarks": "सत्यापित प्रतिलिपि"}
        )
        assert app_res.status_code == 200
        assert app_res.json()["verification_status"] == "VERIFIED"

    # 5. Interactive Official Step Checking
    step_toggle = client.post(
        f"/api/v1/action-plans/{plan_number}/steps/1/toggle",
        json={
            "step_number": 1,
            "scheme_code": "PM_KISAN",
            "is_completed": True,
            "acknowledgement_ref": "UP-PMK-2026-9812",
            "evidence_notes": "CSC Center submission completed"
        }
    )
    assert step_toggle.status_code == 200
    assert step_toggle.json()["is_completed"] is True
    assert step_toggle.json()["acknowledgement_ref"] == "UP-PMK-2026-9812"

    # 6. Farmer-Reported Application Progress Update
    prog_res = client.post(
        f"/api/v1/action-plans/{plan_number}/schemes/PM_KISAN/progress",
        json={
            "scheme_code": "PM_KISAN",
            "status": "APPLICATION_SUBMITTED",
            "application_reference_number": "UP-PMK-2026-9812",
            "farmer_remarks": "Submitted at Tehsil CSC"
        }
    )
    assert prog_res.status_code == 200
    assert prog_res.json()["status"] == "APPLICATION_SUBMITTED"
    assert prog_res.json()["is_government_verified"] is False

    # 7. Departmental Government Verification Recording (and 1-click toggle)
    govt_toggle_res = client.post(
        f"/api/v1/action-plans/{plan_number}/schemes/PM_KISAN/govt-verification/toggle",
        json={"scheme_code": "PM_KISAN", "is_checked": True}
    )
    assert govt_toggle_res.status_code == 200
    assert govt_toggle_res.json()["is_verified"] is True

    govt_res = client.post(
        f"/api/v1/action-plans/{plan_number}/schemes/PM_KISAN/govt-verification",
        json={
            "scheme_code": "PM_KISAN",
            "verification_source": "UP Agriculture DBT Portal Direct Verification",
            "official_reference_number": "SANCTION-UP-2026-09124",
            "status": "GOVERNMENT_VERIFIED",
            "remarks": "Tehsildar land title verified."
        }
    )
    assert govt_res.status_code == 200
    assert govt_res.json()["official_reference_number"] == "SANCTION-UP-2026-09124"

    # 8. Check workflow status now that docs are verified
    wf_after = client.get(f"/api/v1/action-plans/{plan_number}/workflow")
    assert wf_after.status_code == 200
    wf_after_data = wf_after.json()
    assert wf_after_data["can_confirm"] is True
    assert len(wf_after_data["unmet_prerequisites"]) == 0

    # 9. Confirm Action Plan (Generates immutable confirmation)
    confirm_res = client.post(
        f"/api/v1/action-plans/{plan_number}/confirm",
        json={
            "farmer_consent": True,
            "farmer_name": "राम कुमार वर्मा (Ram Kumar Verma)",
            "farmer_mobile": "9876543210"
        }
    )
    assert confirm_res.status_code == 200
    confirm_data = confirm_res.json()
    assert confirm_data["is_confirmed"] is True
    assert confirm_data["summary_ref_id"].startswith("FBS-UP-")
    assert confirm_data["farmer_mobile_masked"] == "******3210"

    # Idempotent re-confirmation returns same record
    confirm_res_idempotent = client.post(
        f"/api/v1/action-plans/{plan_number}/confirm",
        json={"farmer_consent": True}
    )
    assert confirm_res_idempotent.status_code == 200
    assert confirm_res_idempotent.json()["summary_ref_id"] == confirm_data["summary_ref_id"]

    # 10. Download 1-Page Summary PDF
    pdf_res = client.get(f"/api/v1/action-plans/{plan_number}/summary-pdf")
    assert pdf_res.status_code == 200
    assert pdf_res.headers["content-type"] == "application/pdf"
    assert b"%PDF-" in pdf_res.content
    assert len(pdf_res.content) > 3000
