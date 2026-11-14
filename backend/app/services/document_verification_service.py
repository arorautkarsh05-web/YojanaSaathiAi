"""
Document Verification & Farmer Benefit Confirmation Service.
Handles dynamic document requirement resolution, deduplication, magic-byte MIME validation,
secure file storage, reviewer verification lifecycles, and action plan confirmation.
"""

import os
import uuid
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.models import (
    ActionPlan, FarmerProfile, FarmerDocument, DocumentVerificationRecord,
    ActionItemCompletion, FarmerApplicationProgress, BenefitVerificationRecord,
    ActionPlanConfirmation, AuditLog
)
from app.schemas import (
    RequiredDocumentSpec, FarmerDocumentOut, ActionItemCompletionOut,
    FarmerApplicationProgressOut, BenefitVerificationRecordOut,
    ActionPlanConfirmationResponse, WorkflowStageStatus, ActionPlanWorkflowSummaryResponse
)
from app.services.scheme_catalogue import SCHEME_CATALOGUE

STORAGE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "storage", "documents")
os.makedirs(STORAGE_DIR, exist_ok=True)

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

# Magic byte signatures for safe verification
MIME_SIGNATURES = {
    "application/pdf": b"%PDF-",
    "image/jpeg": b"\xFF\xD8\xFF",
    "image/png": b"\x89PNG\r\n\x1a\n",
}

VALID_EXTENSIONS = {
    "application/pdf": ".pdf",
    "image/jpeg": ".jpg",
    "image/png": ".png",
}

REJECTION_REASONS = [
    "दस्तावेज़ स्पष्ट या पढ़ने योग्य नहीं है (Blurred or Unreadable Document)",
    "नाम या व्यक्तिगत विवरण में विसंगति (Name or Profile Mismatch)",
    "दस्तावेज़ की वैधता समाप्त हो चुकी है (Document Expired)",
    "गलत या अधूरा दस्तावेज़ अपलोड किया गया (Incorrect or Incomplete Document)",
    "राजस्व मुहर या डिजिटल हस्ताक्षर अनुपलब्ध (Missing Revenue Seal or Digital Signature)",
    "आधार संख्या अस्पष्ट या गैर-मास्क्ड (Aadhaar Number Unclear or Unmasked)",
]

# Official Document Matrix with deduplication mappings
DOCUMENT_SPECS: Dict[str, Dict[str, Any]] = {
    "doc_khatauni": {
        "title_en": "Land Ownership Record (Khatauni / ROR)",
        "title_hi": "भूमि स्वामित्व अभिलेख (खतौनी / आरओआर)",
        "document_category": "LAND_RECORD",
        "is_mandatory": True,
        "is_aadhaar": False,
        "source_authority": "उत्तर प्रदेश राजस्व परिषद / भूलेख पोर्टल (upbhulekh.gov.in)",
        "notes_hi": "वर्तमान वित्तीय वर्ष की प्रमाणित कंप्यूटरीकृत खतौनी प्रति।",
    },
    "doc_bank_passbook": {
        "title_en": "Bank Passbook / Cancelled Cheque",
        "title_hi": "बैंक पासबुक प्रथम पृष्ठ / रद्द चेक",
        "document_category": "FINANCIAL_PROOF",
        "is_mandatory": True,
        "is_aadhaar": False,
        "source_authority": "राष्ट्रीयकृत या क्षेत्रीय ग्रामीण बैंक शाखा (DBT सक्रिय)",
        "notes_hi": "खाता संख्या, IFSC कोड और किसान का नाम स्पष्ट रूप से दृश्य होना चाहिए। खाता आधार से लिंक (DBT Enabled) होना अनिवार्य है।",
    },
    "doc_aadhaar": {
        "title_en": "Aadhaar Card (Masked Copy Recommended)",
        "title_hi": "आधार कार्ड (मास्क्ड प्रतिलिपि अनुशंसित)",
        "document_category": "IDENTITY_PROOF",
        "is_mandatory": True, # Mandatory only for schemes that legally mandate DBT under Aadhaar Act Sec 7
        "is_aadhaar": True,
        "source_authority": "भारतीय विशिष्ट पहचान प्राधिकरण (UIDAI)",
        "notes_hi": "केवल अंतिम 4 अंक दृश्य हों (उदा. XXXX-XXXX-1234)। संपूर्ण 12-अंकीय आधार साझा करना आवश्यक नहीं है।",
    },
    "doc_photo": {
        "title_en": "Passport Size Photograph",
        "title_hi": "पासपोर्ट आकार का नवीनतम फोटो",
        "document_category": "IDENTITY_PROOF",
        "is_mandatory": True,
        "is_aadhaar": False,
        "source_authority": "स्वयं आवेदक",
        "notes_hi": "सफेद या हल्के रंग की पृष्ठभूमि में हाल ही में खींचा गया स्पष्ट फोटो।",
    },
    "doc_sowing_cert": {
        "title_en": "Crop Sowing Certificate / Girdawari",
        "title_hi": "फसल बुवाई प्रमाण-पत्र / खसरा गिरदावरी",
        "document_category": "CROP_EVIDENCE",
        "is_mandatory": True,
        "is_aadhaar": False,
        "source_authority": "क्षेत्रीय लेखपाल / ग्राम पंचायत कृषि प्राधिकारी",
        "notes_hi": "बीमित या अधिसूचित फसल के रकबे और बुवाई की तिथि का लेखपाल सत्यापन।",
    },
    "doc_caste_cert": {
        "title_en": "Caste Certificate (SC/ST/OBC)",
        "title_hi": "जाति प्रमाण-पत्र (अनु. जाति / जन. जाति / अन्य पिछड़ा वर्ग)",
        "document_category": "SOCIAL_CATEGORY_PROOF",
        "is_mandatory": False,
        "is_aadhaar": False,
        "source_authority": "तहसीलदार / ई-डिस्ट्रिक्ट पोर्टल उत्तर प्रदेश",
        "notes_hi": "विशेष सब्सिडी या प्राथमिकता श्रेणी का लाभ प्राप्त करने हेतु आवश्यक।",
    },
    "doc_soil_sample": {
        "title_en": "Previous Soil Test Report / Sample Slip",
        "title_hi": "पिछली मृदा परीक्षण रिपोर्ट / नमूना रसीद",
        "document_category": "FARM_RECORD",
        "is_mandatory": False,
        "is_aadhaar": False,
        "source_authority": "जिला कृषि प्रयोगशाला / कृषि विज्ञान केंद्र",
        "notes_hi": "यदि पूर्व में मृदा स्वास्थ्य कार्ड बनवाया गया हो तो विवरण दर्ज करें।",
    },
    "doc_announcement_form": {
        "title_en": "Farmer Self-Declaration Form",
        "title_hi": "किसान स्व-घोषणा पत्र",
        "document_category": "DECLARATION",
        "is_mandatory": True,
        "is_aadhaar": False,
        "source_authority": "कृषि विभाग उत्तर प्रदेश (upagriculture.com)",
        "notes_hi": "कृषि यंत्र या सौर पंप अनुदान के लिए विभागीय स्व-घोषणा प्रारूप।",
    }
}

# Scheme to required document mapping
SCHEME_DOCUMENT_MATRIX: Dict[str, List[str]] = {
    "PM_KISAN": ["doc_aadhaar", "doc_khatauni", "doc_bank_passbook"],
    "PMKSY": ["doc_khatauni", "doc_bank_passbook", "doc_aadhaar", "doc_photo"],
    "PMFBY": ["doc_khatauni", "doc_bank_passbook", "doc_sowing_cert", "doc_aadhaar"],
    "KCC": ["doc_khatauni", "doc_bank_passbook", "doc_photo", "doc_aadhaar"],
    "SHC": ["doc_khatauni", "doc_soil_sample"],
    "SMAM": ["doc_khatauni", "doc_bank_passbook", "doc_aadhaar", "doc_photo", "doc_announcement_form"],
}


def get_required_documents_for_schemes(selected_scheme_codes: List[str]) -> List[RequiredDocumentSpec]:
    """
    Computes deduplicated list of required documents for a set of selected schemes.
    Consolidates shared documents (e.g. Khatauni, Bank Passbook, Aadhaar) across schemes.
    """
    doc_schemes_map: Dict[str, List[str]] = {}

    for scheme_code in selected_scheme_codes:
        docs = SCHEME_DOCUMENT_MATRIX.get(scheme_code, ["doc_khatauni", "doc_bank_passbook"])
        for doc_key in docs:
            if doc_key not in doc_schemes_map:
                doc_schemes_map[doc_key] = []
            if scheme_code not in doc_schemes_map[doc_key]:
                doc_schemes_map[doc_key].append(scheme_code)

    specs = []
    for doc_key, applicable_schemes in doc_schemes_map.items():
        spec_info = DOCUMENT_SPECS.get(doc_key, {
            "title_en": doc_key.replace("doc_", "").title(),
            "title_hi": doc_key.replace("doc_", "").title(),
            "document_category": "SUPPORTING_PROOF",
            "is_mandatory": True,
            "is_aadhaar": "aadhaar" in doc_key.lower(),
            "source_authority": "सक्षम प्राधिकारी",
            "notes_hi": "आधिकारिक योजना दिशा-निर्देशानुसार आवश्यक।"
        })

        specs.append(
            RequiredDocumentSpec(
                doc_id_key=doc_key,
                title_en=spec_info["title_en"],
                title_hi=spec_info["title_hi"],
                document_category=spec_info["document_category"],
                is_mandatory=spec_info["is_mandatory"],
                is_aadhaar=spec_info["is_aadhaar"],
                applicable_schemes=applicable_schemes,
                source_authority=spec_info["source_authority"],
                notes_hi=spec_info.get("notes_hi")
            )
        )

    # Sort so mandatory documents and Land/Bank come first
    specs.sort(key=lambda s: (not s.is_mandatory, 0 if "khatauni" in s.doc_id_key else (1 if "bank" in s.doc_id_key else 2)))
    return specs


def validate_file_bytes(content: bytes) -> str:
    """
    Validates file content using magic bytes to prevent MIME spoofing.
    Returns the detected canonical mime type, or raises HTTPException.
    """
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="रिक्त फ़ाइल अपलोड नहीं की जा सकती (Empty file uploaded)."
        )

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="फ़ाइल का आकार 5MB की अनुमत सीमा से अधिक है (File exceeds 5MB maximum limit)."
        )

    # Check magic byte signatures
    if content.startswith(b"%PDF-"):
        return "application/pdf"
    elif content.startswith(b"\xFF\xD8\xFF"):
        return "image/jpeg"
    elif content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"

    raise HTTPException(
        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        detail="अमान्य फ़ाइल प्रारूप। केवल वैध PDF, JPG, या PNG फ़ाइलें ही स्वीकार्य हैं (Only valid PDF, JPG, or PNG files are accepted)."
    )


def save_farmer_document(
    db: Session,
    plan_number: str,
    doc_id_key: str,
    file_bytes: bytes,
    original_filename: str,
    user_id: Optional[str] = None
) -> FarmerDocument:
    """
    Validates file, writes safely with a unique UUID filename outside web root,
    and creates or updates the persistent FarmerDocument record.
    """
    mime_type = validate_file_bytes(file_bytes)
    ext = VALID_EXTENSIONS.get(mime_type, ".bin")
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    dest_path = os.path.join(STORAGE_DIR, unique_filename)

    with open(dest_path, "wb") as f:
        f.write(file_bytes)

    spec_info = DOCUMENT_SPECS.get(doc_id_key, {
        "title_en": doc_id_key.replace("doc_", "").title(),
        "title_hi": doc_id_key.replace("doc_", "").title(),
        "document_category": "SUPPORTING_PROOF",
        "is_aadhaar": "aadhaar" in doc_id_key.lower()
    })

    # Check if a document record already exists for this plan and key
    existing_doc = db.query(FarmerDocument).filter(
        FarmerDocument.plan_number == plan_number,
        FarmerDocument.doc_id_key == doc_id_key
    ).first()

    now = datetime.now(timezone.utc)
    if existing_doc:
        # Mark previous file as replaced
        existing_doc.file_path = dest_path
        existing_doc.file_name_original = original_filename
        existing_doc.file_size_bytes = len(file_bytes)
        existing_doc.mime_type = mime_type
        existing_doc.upload_status = "UPLOADED"
        existing_doc.verification_status = "UNDER_REVIEW"
        existing_doc.rejection_reason = None
        existing_doc.verification_remarks = None
        existing_doc.updated_at = now
        doc_record = existing_doc
    else:
        doc_record = FarmerDocument(
            plan_number=plan_number,
            user_id=user_id,
            doc_id_key=doc_id_key,
            document_category=spec_info["document_category"],
            title_en=spec_info["title_en"],
            title_hi=spec_info["title_hi"],
            file_path=dest_path,
            file_name_original=original_filename,
            file_size_bytes=len(file_bytes),
            mime_type=mime_type,
            upload_status="UPLOADED",
            verification_status="UNDER_REVIEW",
            is_masked_aadhaar=spec_info.get("is_aadhaar", False),
            created_at=now,
            updated_at=now
        )
        db.add(doc_record)

    # Audit log
    audit = AuditLog(
        user_id=user_id,
        action="DOCUMENT_UPLOAD",
        resource_type="FarmerDocument",
        resource_id=doc_record.id,
        metadata_json=json.dumps({
            "plan_number": plan_number,
            "doc_id_key": doc_id_key,
            "filename": original_filename,
            "size": len(file_bytes),
            "mime_type": mime_type
        })
    )
    db.add(audit)
    db.commit()
    db.refresh(doc_record)
    return doc_record


def review_farmer_document(
    db: Session,
    document_id: str,
    action: str, # APPROVE, REJECT, REQUEST_REUPLOAD
    reviewer_id: Optional[str] = None,
    rejection_reason: Optional[str] = None,
    remarks: Optional[str] = None
) -> FarmerDocument:
    """
    Performs reviewer verification action on an uploaded document.
    """
    doc = db.query(FarmerDocument).filter(FarmerDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="दस्तावेज़ नहीं मिला (Document record not found).")

    action_upper = action.upper()
    now = datetime.now(timezone.utc)

    if action_upper == "APPROVE":
        resulting_status = "VERIFIED"
        doc.verification_status = "VERIFIED"
        doc.verified_by_user_id = reviewer_id or "OFFICIAL_REVIEWER"
        doc.verified_at = now
        doc.rejection_reason = None
        doc.verification_remarks = remarks or "दस्तावेज़ की स्पष्टता एवं प्रामाणिकता सत्यापित की गई।"
    elif action_upper == "REJECT":
        if not rejection_reason:
            raise HTTPException(
                status_code=400,
                detail="दस्तावेज़ अस्वीकार करने के लिए कारण अनिवार्य है (Rejection reason is required)."
            )
        resulting_status = "REJECTED"
        doc.verification_status = "REJECTED"
        doc.rejection_reason = rejection_reason
        doc.verification_remarks = remarks
        doc.verified_at = now
        doc.verified_by_user_id = reviewer_id or "OFFICIAL_REVIEWER"
    elif action_upper == "REQUEST_REUPLOAD":
        resulting_status = "REUPLOAD_REQUIRED"
        doc.verification_status = "REUPLOAD_REQUIRED"
        doc.rejection_reason = rejection_reason or "स्पष्ट प्रति पुनः अपलोड करने का अनुरोध"
        doc.verification_remarks = remarks
        doc.verified_at = now
    else:
        raise HTTPException(status_code=400, detail=f"अमान्य समीक्षा क्रिया: {action}")

    doc.updated_at = now

    record = DocumentVerificationRecord(
        document_id=doc.id,
        reviewer_id=reviewer_id or "OFFICIAL_REVIEWER",
        action=action_upper,
        resulting_status=resulting_status,
        remarks=remarks or rejection_reason,
        created_at=now
    )
    db.add(record)

    audit = AuditLog(
        user_id=reviewer_id,
        action=f"DOCUMENT_VERIFY_{action_upper}",
        resource_type="FarmerDocument",
        resource_id=doc.id,
        metadata_json=json.dumps({
            "plan_number": doc.plan_number,
            "resulting_status": resulting_status,
            "reason": rejection_reason,
            "remarks": remarks
        })
    )
    db.add(audit)
    db.commit()
    db.refresh(doc)
    return doc


def toggle_official_step(
    db: Session,
    plan_number: str,
    step_number: int,
    scheme_code: str,
    is_completed: bool,
    acknowledgement_ref: Optional[str] = None,
    evidence_notes: Optional[str] = None,
    title_en: Optional[str] = None,
    title_hi: Optional[str] = None
) -> ActionItemCompletion:
    """
    Toggles official action step completion state and logs evidence.
    """
    record = db.query(ActionItemCompletion).filter(
        ActionItemCompletion.plan_number == plan_number,
        ActionItemCompletion.step_number == step_number
    ).first()

    now = datetime.now(timezone.utc)
    if record:
        record.is_completed = is_completed
        record.completed_at = now if is_completed else None
        if acknowledgement_ref is not None:
            record.acknowledgement_ref = acknowledgement_ref
        if evidence_notes is not None:
            record.evidence_notes = evidence_notes
    else:
        record = ActionItemCompletion(
            plan_number=plan_number,
            step_number=step_number,
            scheme_code=scheme_code,
            title_en=title_en or f"Step {step_number}",
            title_hi=title_hi or f"चरण {step_number}",
            is_completed=is_completed,
            completed_at=now if is_completed else None,
            acknowledgement_ref=acknowledgement_ref,
            evidence_notes=evidence_notes,
            created_at=now
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return record


def update_farmer_progress(
    db: Session,
    plan_number: str,
    scheme_code: str,
    status: str,
    application_ref: Optional[str] = None,
    remarks: Optional[str] = None
) -> FarmerApplicationProgress:
    """
    Records farmer-reported application lifecycle progress for a specific scheme.
    """
    record = db.query(FarmerApplicationProgress).filter(
        FarmerApplicationProgress.plan_number == plan_number,
        FarmerApplicationProgress.scheme_code == scheme_code
    ).first()

    now = datetime.now(timezone.utc)
    if record:
        record.status = status
        if application_ref is not None:
            record.application_reference_number = application_ref
        if remarks is not None:
            record.farmer_remarks = remarks
        record.updated_at = now
    else:
        record = FarmerApplicationProgress(
            plan_number=plan_number,
            scheme_code=scheme_code,
            status=status,
            application_reference_number=application_ref,
            farmer_remarks=remarks,
            is_government_verified=False,
            updated_at=now
        )
        db.add(record)

    db.commit()
    db.refresh(record)
    return record


def record_government_verification(
    db: Session,
    plan_number: str,
    scheme_code: str,
    verification_source: str,
    official_reference_number: str,
    status: str = "GOVERNMENT_VERIFIED",
    reviewer_id: Optional[str] = None,
    remarks: Optional[str] = None
) -> BenefitVerificationRecord:
    """
    Records authoritative government verification (e.g. from official DBT portal query or sanction order).
    """
    now = datetime.now(timezone.utc)
    record = BenefitVerificationRecord(
        plan_number=plan_number,
        scheme_code=scheme_code,
        verification_source=verification_source,
        official_reference_number=official_reference_number,
        status=status,
        verified_at=now,
        reviewer_id=reviewer_id,
        remarks=remarks
    )
    db.add(record)

    # Also update FarmerApplicationProgress flag
    prog = db.query(FarmerApplicationProgress).filter(
        FarmerApplicationProgress.plan_number == plan_number,
        FarmerApplicationProgress.scheme_code == scheme_code
    ).first()
    if prog:
        prog.is_government_verified = True

    db.commit()
    db.refresh(record)
    return record


def check_confirmation_prerequisites(
    db: Session,
    plan_number: str,
    selected_scheme_codes: List[str]
) -> Tuple[bool, List[str]]:
    """
    Verifies that all prerequisites for final action plan confirmation are met:
    1. All mandatory documents must be uploaded and have status 'VERIFIED'.
    """
    required_specs = get_required_documents_for_schemes(selected_scheme_codes)
    mandatory_specs = [s for s in required_specs if s.is_mandatory]

    uploaded_docs = db.query(FarmerDocument).filter(
        FarmerDocument.plan_number == plan_number
    ).all()
    uploaded_map = {d.doc_id_key: d for d in uploaded_docs}

    unmet = []
    for spec in mandatory_specs:
        doc = uploaded_map.get(spec.doc_id_key)
        if not doc:
            unmet.append(f"{spec.title_hi}: अभी तक अपलोड नहीं किया गया है (Not uploaded yet).")
        elif doc.verification_status != "VERIFIED":
            status_desc = {
                "UNDER_REVIEW": "समीक्षाधीन है (Under review)",
                "REJECTED": f"अस्वीकृत है ({doc.rejection_reason or 'पुनः जांच आवश्यक'})",
                "REUPLOAD_REQUIRED": "पुनः अपलोड आवश्यक है (Re-upload requested)",
                "NOT_UPLOADED": "अपलोड नहीं किया गया"
            }.get(doc.verification_status, doc.verification_status)
            unmet.append(f"{spec.title_hi}: सत्यापन लंबित है ({status_desc}).")

    can_confirm = len(unmet) == 0
    return can_confirm, unmet


def confirm_action_plan(
    db: Session,
    plan_number: str,
    farmer_consent: bool,
    farmer_name: Optional[str] = None,
    farmer_mobile: Optional[str] = None
) -> ActionPlanConfirmation:
    """
    Confirms the completed action plan if prerequisites are met.
    Enforces idempotency and generates an immutable confirmation record.
    """
    # Check if already confirmed
    existing = db.query(ActionPlanConfirmation).filter(
        ActionPlanConfirmation.plan_number == plan_number
    ).first()
    if existing:
        return existing

    if not farmer_consent:
        raise HTTPException(
            status_code=400,
            detail="कार्य योजना संपुष्ट करने के लिए किसान की सहमति अनिवार्य है (Farmer consent is required)."
        )

    # Retrieve selected scheme codes from ActionPlan or fallback to all active
    plan = db.query(ActionPlan).filter(ActionPlan.plan_number == plan_number).first()
    selected_codes = []
    if plan and plan.selected_schemes_json:
        selected_codes = json.loads(plan.selected_schemes_json)

    if not selected_codes:
        # Default active UP schemes if plan was guest or created in-memory
        selected_codes = ["PM_KISAN", "PMKSY", "PMFBY"]

    can_confirm, unmet = check_confirmation_prerequisites(db, plan_number, selected_codes)
    if not can_confirm:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "कार्य योजना संपुष्ट करने से पहले सभी अनिवार्य दस्तावेज़ों का सत्यापन आवश्यक है (All mandatory documents must be verified before confirmation).",
                "unmet_prerequisites": unmet
            }
        )

    # Mask mobile number: e.g. "9876543210" -> "******3210"
    masked_mobile = None
    if farmer_mobile and len(farmer_mobile) >= 4:
        clean = "".join([c for c in farmer_mobile if c.isdigit()])
        if len(clean) >= 4:
            masked_mobile = f"{'*' * (len(clean) - 4)}{clean[-4:]}"

    summary_ref_id = f"FBS-UP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    now = datetime.now(timezone.utc)

    declaration_text = (
        "मैं एतद्द्वारा घोषणा करता/करती हूँ कि योजना साथी AI द्वारा प्रस्तुत पात्रता एवं दस्तावेज़ दिशा-निर्देशों "
        "को मैंने भली-भांति समझ लिया है। यह संक्षेप एक स्वतंत्र तैयारी योजना है। मैं समझता/समझती हूँ कि आधिकारिक "
        "अनुदान एवं लाभ की अंतिम स्वीकृति सक्षम सरकारी विभाग के सत्यापन पर निर्भर है।"
    )

    confirmation = ActionPlanConfirmation(
        plan_number=plan_number,
        summary_ref_id=summary_ref_id,
        farmer_consent=True,
        declaration_text=declaration_text,
        farmer_name=farmer_name or "आवेदक किसान",
        farmer_mobile_masked=masked_mobile,
        prerequisites_snapshot_json=json.dumps({
            "selected_schemes": selected_codes,
            "confirmed_at": now.isoformat(),
            "policy_version": "3.0"
        }),
        policy_version="3.0",
        confirmed_at=now
    )
    db.add(confirmation)

    audit = AuditLog(
        user_id=None,
        action="ACTION_PLAN_CONFIRMED",
        resource_type="ActionPlanConfirmation",
        resource_id=confirmation.id,
        metadata_json=json.dumps({
            "plan_number": plan_number,
            "summary_ref_id": summary_ref_id
        })
    )
    db.add(audit)
    db.commit()
    db.refresh(confirmation)
    return confirmation


def get_action_plan_workflow_summary(
    db: Session,
    plan_number: str,
    selected_scheme_codes: Optional[List[str]] = None
) -> ActionPlanWorkflowSummaryResponse:
    """
    Computes complete 7-stage workflow status for the given action plan.
    """
    # If not provided, fetch from ActionPlan
    if not selected_scheme_codes:
        plan = db.query(ActionPlan).filter(ActionPlan.plan_number == plan_number).first()
        if plan and plan.selected_schemes_json:
            selected_scheme_codes = json.loads(plan.selected_schemes_json)
        else:
            selected_scheme_codes = ["PM_KISAN", "PMKSY", "PMFBY"]

    required_specs = get_required_documents_for_schemes(selected_scheme_codes)
    uploaded_docs = db.query(FarmerDocument).filter(
        FarmerDocument.plan_number == plan_number
    ).all()
    uploaded_map = {d.doc_id_key: d for d in uploaded_docs}

    action_steps = db.query(ActionItemCompletion).filter(
        ActionItemCompletion.plan_number == plan_number
    ).order_by(ActionItemCompletion.step_number).all()

    progress_records = db.query(FarmerApplicationProgress).filter(
        FarmerApplicationProgress.plan_number == plan_number
    ).all()

    govt_verifications = db.query(BenefitVerificationRecord).filter(
        BenefitVerificationRecord.plan_number == plan_number
    ).all()

    confirmation = db.query(ActionPlanConfirmation).filter(
        ActionPlanConfirmation.plan_number == plan_number
    ).first()

    can_confirm, unmet = check_confirmation_prerequisites(db, plan_number, selected_scheme_codes)

    # Compute stage statuses
    total_req_mandatory = len([s for s in required_specs if s.is_mandatory])
    verified_mandatory_count = len([
        s for s in required_specs
        if s.is_mandatory and uploaded_map.get(s.doc_id_key) and uploaded_map[s.doc_id_key].verification_status == "VERIFIED"
    ])

    stage4_status = "COMPLETED" if (verified_mandatory_count == total_req_mandatory and total_req_mandatory > 0) else "ACTIVE"
    stage5_completed_count = len([s for s in action_steps if s.is_completed])
    stage5_status = "COMPLETED" if (stage5_completed_count > 0 and stage5_completed_count >= len(action_steps)) else ("ACTIVE" if stage4_status == "COMPLETED" else "PENDING")
    
    has_progress = len([p for p in progress_records if p.status != "NOT_YET_APPLIED"]) > 0
    stage6_status = "ACTIVE" if has_progress else "PENDING"
    stage7_status = "COMPLETED" if len(govt_verifications) > 0 else "PENDING"

    stages = [
        WorkflowStageStatus(stage_number=1, title_en="Farmer Profile", title_hi="प्रोफाइल विवरण", status="COMPLETED", detail="सत्यापित विवरण"),
        WorkflowStageStatus(stage_number=2, title_en="Eligibility Assessment", title_hi="पात्रता जाँच", status="COMPLETED", detail="नियम मूल्यांकन पूर्ण"),
        WorkflowStageStatus(stage_number=3, title_en="Missing Info Resolution", title_hi="छूटी जानकारी", status="COMPLETED", detail="आवश्यकता पहचानी"),
        WorkflowStageStatus(
            stage_number=4,
            title_en="Document Verification",
            title_hi="दस्तावेज़ सत्यापन",
            status=stage4_status,
            detail=f"{verified_mandatory_count}/{total_req_mandatory} अनिवार्य सत्यापित"
        ),
        WorkflowStageStatus(
            stage_number=5,
            title_en="Official Next Steps",
            title_hi="आधिकारिक आवेदन",
            status=stage5_status,
            detail=f"{stage5_completed_count}/{len(action_steps)} कदम पूरे" if action_steps else "आधिकारिक पोर्टल"
        ),
        WorkflowStageStatus(
            stage_number=6,
            title_en="Farmer Progress",
            title_hi="किसान प्रगति",
            status=stage6_status,
            detail="स्वयं दर्ज स्थिति"
        ),
        WorkflowStageStatus(
            stage_number=7,
            title_en="Benefit Confirmation",
            title_hi="लाभ संपुष्टि",
            status=stage7_status,
            detail="विभागीय सत्यापन" if len(govt_verifications) > 0 else "सत्यापन प्रतीक्षित"
        ),
    ]

    confirmation_resp = None
    if confirmation:
        confirmation_resp = ActionPlanConfirmationResponse(
            summary_ref_id=confirmation.summary_ref_id,
            plan_number=confirmation.plan_number,
            farmer_consent=confirmation.farmer_consent,
            declaration_text=confirmation.declaration_text,
            farmer_name=confirmation.farmer_name,
            farmer_mobile_masked=confirmation.farmer_mobile_masked,
            policy_version=confirmation.policy_version,
            confirmed_at=confirmation.confirmed_at,
            is_confirmed=True
        )

    return ActionPlanWorkflowSummaryResponse(
        plan_number=plan_number,
        stages=stages,
        required_documents=required_specs,
        uploaded_documents=[
            FarmerDocumentOut(
                id=d.id,
                plan_number=d.plan_number,
                doc_id_key=d.doc_id_key,
                document_category=d.document_category,
                title_en=d.title_en,
                title_hi=d.title_hi,
                file_name_original=d.file_name_original,
                file_size_bytes=d.file_size_bytes,
                mime_type=d.mime_type,
                upload_status=d.upload_status,
                verification_status=d.verification_status,
                rejection_reason=d.rejection_reason,
                verification_remarks=d.verification_remarks,
                verified_at=d.verified_at,
                is_masked_aadhaar=d.is_masked_aadhaar,
                created_at=d.created_at,
                updated_at=d.updated_at
            ) for d in uploaded_docs
        ],
        action_steps=[
            ActionItemCompletionOut(
                id=s.id,
                plan_number=s.plan_number,
                step_number=s.step_number,
                scheme_code=s.scheme_code,
                title_en=s.title_en,
                title_hi=s.title_hi,
                is_completed=s.is_completed,
                completed_at=s.completed_at,
                acknowledgement_ref=s.acknowledgement_ref,
                evidence_notes=s.evidence_notes
            ) for s in action_steps
        ],
        application_progress=[
            FarmerApplicationProgressOut(
                id=p.id,
                plan_number=p.plan_number,
                scheme_code=p.scheme_code,
                status=p.status,
                application_reference_number=p.application_reference_number,
                farmer_remarks=p.farmer_remarks,
                supporting_document_name=p.supporting_document_name,
                is_government_verified=p.is_government_verified,
                updated_at=p.updated_at
            ) for p in progress_records
        ],
        government_verifications=[
            BenefitVerificationRecordOut(
                id=g.id,
                plan_number=g.plan_number,
                scheme_code=g.scheme_code,
                verification_source=g.verification_source,
                official_reference_number=g.official_reference_number,
                status=g.status,
                verified_at=g.verified_at,
                remarks=g.remarks
            ) for g in govt_verifications
        ],
        confirmation=confirmation_resp,
        can_confirm=can_confirm,
        unmet_prerequisites=unmet
    )
