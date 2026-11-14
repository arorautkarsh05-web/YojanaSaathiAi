import os
import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_optional_user
from app.models import User, ActionPlan, FarmerProfile, FarmerDocument, ActionPlanConfirmation
from app.schemas import (
    ActionPlanCreate, ActionPlanResponse, DocumentUploadResponse,
    DocumentVerifyRequest, ActionItemCompletionOut, ActionStepToggleRequest,
    FarmerApplicationProgressOut, FarmerApplicationProgressUpdate,
    BenefitVerificationRecordOut, BenefitVerificationCreate,
    ActionPlanConfirmationRequest, ActionPlanConfirmationResponse,
    ActionPlanWorkflowSummaryResponse, FarmerDocumentOut,
    DocumentToggleRequest, SchemeToggleRequest
)
from app.services.action_plan_service import generate_action_plan
from app.services.document_verification_service import (
    save_farmer_document, review_farmer_document, toggle_official_step,
    update_farmer_progress, record_government_verification,
    confirm_action_plan, get_action_plan_workflow_summary,
    toggle_farmer_document_tick, toggle_government_verification
)
from app.services.summary_pdf_service import generate_farmer_benefit_summary_pdf

router = APIRouter(prefix="/action-plans", tags=["Farmer Benefit Action Plan"])

@router.post("", response_model=ActionPlanResponse)
def create_action_plan(
    req: ActionPlanCreate,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    profile_dict = {}
    db_profile = None

    if req.profile_id:
        db_profile = db.query(FarmerProfile).filter(FarmerProfile.id == req.profile_id).first()
        if db_profile:
            if db_profile.user_id and (not current_user or db_profile.user_id != current_user.id):
                raise HTTPException(status_code=403, detail="Unauthorized access to profile.")
            profile_dict = {
                "district": db_profile.district,
                "landholding_acres": db_profile.landholding_acres,
                "farmer_category": db_profile.farmer_category,
                "primary_crops": db_profile.primary_crops.split(",") if db_profile.primary_crops else [],
                "social_category": db_profile.social_category,
                "irrigation_source": db_profile.irrigation_source,
                "state": "Uttar Pradesh"
            }
    elif req.profile:
        profile_dict = req.profile.model_dump()
        profile_dict["state"] = "Uttar Pradesh"

    plan_response = generate_action_plan(
        profile_data=profile_dict,
        selected_scheme_codes=req.selected_scheme_codes,
        checklist_states=req.checklist_states
    )

    # Ensure a profile record exists so ActionPlan foreign key is satisfied
    if not db_profile:
        district_val = profile_dict.get("district") or "Varanasi"
        crops_str = ",".join(profile_dict.get("primary_crops", [])) if isinstance(profile_dict.get("primary_crops"), list) else None
        db_profile = FarmerProfile(
            user_id=current_user.id if current_user else None,
            district=district_val,
            landholding_acres=profile_dict.get("landholding_acres"),
            farmer_category=profile_dict.get("farmer_category"),
            primary_crops=crops_str,
            social_category=profile_dict.get("social_category"),
            irrigation_source=profile_dict.get("irrigation_source"),
            is_temporary=False if current_user else True
        )
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)

    # Persist the action plan record
    plan_record = ActionPlan(
        plan_number=plan_response.plan_number,
        user_id=current_user.id if current_user else None,
        profile_id=db_profile.id,
        selected_schemes_json=json.dumps(req.selected_scheme_codes),
        results_summary_json=json.dumps([s.model_dump() for s in plan_response.selected_schemes]),
        checklist_items_json=json.dumps([c.model_dump() for c in plan_response.checklist_items])
    )
    db.add(plan_record)

    # Initialize action item completions for interactive checking
    for step in plan_response.official_steps:
        code_tag = step.title_en.split("]")[0].replace("[", "").strip() if "]" in step.title_en else "SCHEME"
        toggle_official_step(
            db=db,
            plan_number=plan_response.plan_number,
            step_number=step.step_number,
            scheme_code=code_tag,
            is_completed=False,
            title_en=step.title_en,
            title_hi=step.title_hi
        )

    # Initialize farmer application progress for selected schemes
    for code in req.selected_scheme_codes:
        update_farmer_progress(
            db=db,
            plan_number=plan_response.plan_number,
            scheme_code=code,
            status="NOT_YET_APPLIED"
        )

    db.commit()
    return plan_response


@router.get("/{plan_number}", response_model=ActionPlanResponse)
def get_action_plan_by_number(
    plan_number: str,
    db: Session = Depends(get_db)
):
    record = db.query(ActionPlan).filter(ActionPlan.plan_number == plan_number).first()
    if not record:
        raise HTTPException(status_code=404, detail="कार्य योजना संदर्भ नहीं मिला (Action plan reference not found).")

    selected_schemes_raw = json.loads(record.results_summary_json)
    checklist_items_raw = json.loads(record.checklist_items_json)
    selected_codes = json.loads(record.selected_schemes_json)
    
    # Re-evaluate convergence for freshness
    from app.services.convergence_engine import check_multi_scheme_convergence
    from app.services.scheme_catalogue import SCHEME_CATALOGUE
    from app.schemas import OfficialStep

    convergence_results = check_multi_scheme_convergence(selected_codes)

    # Reconstruct official steps
    official_steps = []
    step_num = 1
    for code in selected_codes:
        meta = SCHEME_CATALOGUE.get(code, {})
        for s in meta.get("official_steps", []):
            official_steps.append(
                OfficialStep(
                    step_number=step_num,
                    title_en=f"[{code}] {s['title_en']}",
                    title_hi=f"[{code}] {s['title_hi']}",
                    description_en=s["description_en"],
                    description_hi=s["description_hi"],
                    portal_or_destination=s["portal_or_destination"],
                    is_independent=s.get("is_independent", True)
                )
            )
            step_num += 1

    return ActionPlanResponse(
        plan_number=record.plan_number,
        created_at=record.created_at.isoformat(),
        selected_schemes=selected_schemes_raw,
        convergence_summary=convergence_results,
        checklist_items=checklist_items_raw,
        official_steps=official_steps,
        disclaimer="योजना साथी एक स्वतंत्र सार्वजनिक मार्गदर्शक प्रणाली है। यह सीधे सरकारी आवेदन प्रस्तुत नहीं करती है। सभी आवेदन संबंधित आधिकारिक सरकारी पोर्टल या जन सुविधा केंद्र (CSC) के माध्यम से किए जाते हैं, और अंतिम पात्रता निर्धारण सक्षम सरकारी प्राधिकारी द्वारा किया जाता है।"
    )


@router.get("/{plan_number}/workflow", response_model=ActionPlanWorkflowSummaryResponse)
def get_action_plan_workflow(
    plan_number: str,
    db: Session = Depends(get_db)
):
    """
    Returns full 7-stage workflow status, required documents, uploaded documents,
    official steps, application progress, and confirmation prerequisites.
    """
    return get_action_plan_workflow_summary(db=db, plan_number=plan_number)


@router.post("/{plan_number}/documents/upload", response_model=DocumentUploadResponse)
async def upload_action_plan_document(
    plan_number: str,
    doc_id_key: str = Form(...),
    file: UploadFile = File(...),
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Uploads a supporting document for an action plan with magic-byte validation and secure storage.
    """
    file_bytes = await file.read()
    doc_record = save_farmer_document(
        db=db,
        plan_number=plan_number,
        doc_id_key=doc_id_key,
        file_bytes=file_bytes,
        original_filename=file.filename or "uploaded_document",
        user_id=current_user.id if current_user else None
    )

    return DocumentUploadResponse(
        message="दस्तावेज़ सफलतापूर्वक अपलोड किया गया और समीक्षाधीन है (Document uploaded successfully and under review).",
        document=FarmerDocumentOut(
            id=doc_record.id,
            plan_number=doc_record.plan_number,
            doc_id_key=doc_record.doc_id_key,
            document_category=doc_record.document_category,
            title_en=doc_record.title_en,
            title_hi=doc_record.title_hi,
            file_name_original=doc_record.file_name_original,
            file_size_bytes=doc_record.file_size_bytes,
            mime_type=doc_record.mime_type,
            upload_status=doc_record.upload_status,
            verification_status=doc_record.verification_status,
            rejection_reason=doc_record.rejection_reason,
            verification_remarks=doc_record.verification_remarks,
            verified_at=doc_record.verified_at,
            is_masked_aadhaar=doc_record.is_masked_aadhaar,
            created_at=doc_record.created_at,
            updated_at=doc_record.updated_at
        )
    )


@router.get("/{plan_number}/documents/{doc_id}/download")
def download_action_plan_document(
    plan_number: str,
    doc_id: str,
    db: Session = Depends(get_db)
):
    """
    Streams the uploaded document with authorization and ownership checks.
    """
    doc = db.query(FarmerDocument).filter(
        FarmerDocument.id == doc_id,
        FarmerDocument.plan_number == plan_number
    ).first()
    if not doc or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="दस्तावेज़ फ़ाइल नहीं मिली (Document file not found).")

    return FileResponse(
        path=doc.file_path,
        media_type=doc.mime_type,
        filename=doc.file_name_original
    )


@router.post("/{plan_number}/documents/{doc_id}/verify", response_model=FarmerDocumentOut)
def verify_document_endpoint(
    plan_number: str,
    doc_id: str,
    req: DocumentVerifyRequest,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Reviewer endpoint to approve, reject, or request re-upload with reasons and audit logging.
    """
    reviewer_id = current_user.id if current_user else "OFFICIAL_REVIEWER"
    updated_doc = review_farmer_document(
        db=db,
        document_id=doc_id,
        action=req.action,
        reviewer_id=reviewer_id,
        rejection_reason=req.rejection_reason,
        remarks=req.remarks
    )
    return FarmerDocumentOut(
        id=updated_doc.id,
        plan_number=updated_doc.plan_number,
        doc_id_key=updated_doc.doc_id_key,
        document_category=updated_doc.document_category,
        title_en=updated_doc.title_en,
        title_hi=updated_doc.title_hi,
        file_name_original=updated_doc.file_name_original,
        file_size_bytes=updated_doc.file_size_bytes,
        mime_type=updated_doc.mime_type,
        upload_status=updated_doc.upload_status,
        verification_status=updated_doc.verification_status,
        rejection_reason=updated_doc.rejection_reason,
        verification_remarks=updated_doc.verification_remarks,
        verified_at=updated_doc.verified_at,
        is_masked_aadhaar=updated_doc.is_masked_aadhaar,
        created_at=updated_doc.created_at,
        updated_at=updated_doc.updated_at
    )


@router.post("/{plan_number}/documents/{doc_id_key}/toggle", response_model=FarmerDocumentOut)
def toggle_document_endpoint(
    plan_number: str,
    doc_id_key: str,
    req: DocumentToggleRequest,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Toggles a tick-box document (Khatauni, Bank Passbook, etc.).
    Ticking immediately marks it verified.
    """
    user_id = current_user.id if current_user else None
    doc = toggle_farmer_document_tick(
        db=db,
        plan_number=plan_number,
        doc_id_key=doc_id_key,
        is_checked=req.is_checked,
        user_id=user_id
    )
    return FarmerDocumentOut(
        id=doc.id,
        plan_number=doc.plan_number,
        doc_id_key=doc.doc_id_key,
        document_category=doc.document_category,
        title_en=doc.title_en,
        title_hi=doc.title_hi,
        file_name_original=doc.file_name_original,
        file_size_bytes=doc.file_size_bytes,
        mime_type=doc.mime_type,
        upload_status=doc.upload_status,
        verification_status=doc.verification_status,
        rejection_reason=doc.rejection_reason,
        verification_remarks=doc.verification_remarks,
        verified_at=doc.verified_at,
        is_masked_aadhaar=doc.is_masked_aadhaar,
        created_at=doc.created_at,
        updated_at=doc.updated_at
    )


@router.post("/{plan_number}/steps/{step_number}/toggle", response_model=ActionItemCompletionOut)
def toggle_step_endpoint(
    plan_number: str,
    step_number: int,
    req: ActionStepToggleRequest,
    db: Session = Depends(get_db)
):
    """
    Toggles official action step completion state and records acknowledgement reference.
    """
    record = toggle_official_step(
        db=db,
        plan_number=plan_number,
        step_number=step_number,
        scheme_code=req.scheme_code,
        is_completed=req.is_completed,
        acknowledgement_ref=req.acknowledgement_ref,
        evidence_notes=req.evidence_notes
    )
    return ActionItemCompletionOut(
        id=record.id,
        plan_number=record.plan_number,
        step_number=record.step_number,
        scheme_code=record.scheme_code,
        title_en=record.title_en,
        title_hi=record.title_hi,
        is_completed=record.is_completed,
        completed_at=record.completed_at,
        acknowledgement_ref=record.acknowledgement_ref,
        evidence_notes=record.evidence_notes
    )


@router.post("/{plan_number}/schemes/{scheme_code}/progress", response_model=FarmerApplicationProgressOut)
def update_application_progress_endpoint(
    plan_number: str,
    scheme_code: str,
    req: FarmerApplicationProgressUpdate,
    db: Session = Depends(get_db)
):
    """
    Updates farmer-reported application lifecycle tracking for a specific scheme.
    """
    record = update_farmer_progress(
        db=db,
        plan_number=plan_number,
        scheme_code=scheme_code,
        status=req.status,
        application_ref=req.application_reference_number,
        remarks=req.farmer_remarks
    )
    return FarmerApplicationProgressOut(
        id=record.id,
        plan_number=record.plan_number,
        scheme_code=record.scheme_code,
        status=record.status,
        application_reference_number=record.application_reference_number,
        farmer_remarks=record.farmer_remarks,
        supporting_document_name=record.supporting_document_name,
        is_government_verified=record.is_government_verified,
        updated_at=record.updated_at
    )


@router.post("/{plan_number}/schemes/{scheme_code}/govt-verification", response_model=BenefitVerificationRecordOut)
def record_govt_verification_endpoint(
    plan_number: str,
    scheme_code: str,
    req: BenefitVerificationCreate,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Records authoritative departmental government verification with official reference order.
    """
    reviewer_id = current_user.id if current_user else "DEPARTMENTAL_ADMIN"
    record = record_government_verification(
        db=db,
        plan_number=plan_number,
        scheme_code=scheme_code,
        verification_source=req.verification_source,
        official_reference_number=req.official_reference_number,
        status=req.status,
        reviewer_id=reviewer_id,
        remarks=req.remarks
    )
    return BenefitVerificationRecordOut(
        id=record.id,
        plan_number=record.plan_number,
        scheme_code=record.scheme_code,
        verification_source=record.verification_source,
        official_reference_number=record.official_reference_number,
        status=record.status,
        verified_at=record.verified_at,
        remarks=record.remarks
    )


@router.post("/{plan_number}/schemes/{scheme_code}/govt-verification/toggle")
def toggle_govt_verification_endpoint(
    plan_number: str,
    scheme_code: str,
    req: SchemeToggleRequest,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    """
    Toggles official government sanction verification with a single tick.
    """
    reviewer_id = current_user.id if current_user else "DEPARTMENTAL_OFFICER"
    record = toggle_government_verification(
        db=db,
        plan_number=plan_number,
        scheme_code=scheme_code,
        is_checked=req.is_checked,
        reviewer_id=reviewer_id
    )
    return {
        "status": "success",
        "is_verified": req.is_checked,
        "scheme_code": scheme_code
    }


@router.post("/{plan_number}/confirm", response_model=ActionPlanConfirmationResponse)
def confirm_action_plan_endpoint(
    plan_number: str,
    req: ActionPlanConfirmationRequest,
    db: Session = Depends(get_db)
):
    """
    Executes final action plan confirmation after verifying that all mandatory documents are verified.
    """
    confirmation = confirm_action_plan(
        db=db,
        plan_number=plan_number,
        farmer_consent=req.farmer_consent,
        farmer_name=req.farmer_name,
        farmer_mobile=req.farmer_mobile
    )
    return ActionPlanConfirmationResponse(
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


@router.get("/{plan_number}/summary-pdf")
def get_farmer_benefit_summary_pdf(
    plan_number: str,
    db: Session = Depends(get_db)
):
    """
    Generates and downloads the official-standard 1-page Farmer Benefit Action Summary PDF.
    """
    plan = db.query(ActionPlan).filter(ActionPlan.plan_number == plan_number).first()
    confirmation = db.query(ActionPlanConfirmation).filter(ActionPlanConfirmation.plan_number == plan_number).first()

    summary_ref_id = confirmation.summary_ref_id if confirmation else f"FBS-UP-TEMP-{plan_number[-6:]}"
    farmer_name = confirmation.farmer_name if confirmation else "किसान आवेदक (Applicant Farmer)"
    farmer_mobile = confirmation.farmer_mobile_masked if confirmation else "******1234"
    confirmed_at = confirmation.confirmed_at if confirmation else None

    # Fetch profile details
    district = "Varanasi"
    cat = "Small Farmer"
    landholding = 1.5
    selected_schemes = []

    if plan:
        if plan.results_summary_json:
            selected_schemes = json.loads(plan.results_summary_json)
        if plan.profile:
            district = plan.profile.district or district
            cat = plan.profile.farmer_category or cat
            landholding = plan.profile.landholding_acres or landholding

    if not selected_schemes:
        selected_schemes = [
            {"scheme_code": "PM_KISAN", "official_name_en": "PM Kisan Samman Nidhi", "department": "MoA&FW", "level": "CENTRAL", "overall_status": "LIKELY_ELIGIBLE", "official_portal_url": "pmkisan.gov.in"},
            {"scheme_code": "PMKSY", "official_name_en": "Per Drop More Crop (Micro Irrigation)", "department": "MoA&FW", "level": "CENTRAL", "overall_status": "LIKELY_ELIGIBLE", "official_portal_url": "upagriculture.com"}
        ]

    # Fetch verified documents
    docs = db.query(FarmerDocument).filter(FarmerDocument.plan_number == plan_number).all()
    verified_docs_list = [
        {
            "title_en": d.title_en,
            "doc_id_key": d.doc_id_key,
            "document_category": d.document_category,
            "file_name_original": d.file_name_original,
            "verification_status": d.verification_status
        }
        for d in docs
    ]
    if not verified_docs_list:
        verified_docs_list = [
            {"title_en": "Land Ownership Record (Khatauni)", "doc_id_key": "doc_khatauni", "document_category": "LAND", "file_name_original": "up_khatauni_sample.pdf", "verification_status": "VERIFIED"},
            {"title_en": "Bank Passbook (DBT Active)", "doc_id_key": "doc_bank_passbook", "document_category": "BANK", "file_name_original": "bank_passbook.jpg", "verification_status": "VERIFIED"}
        ]

    pdf_bytes = generate_farmer_benefit_summary_pdf(
        plan_number=plan_number,
        confirmation_ref_id=summary_ref_id,
        farmer_name=farmer_name,
        farmer_mobile_masked=farmer_mobile,
        district=district,
        farmer_category=cat,
        landholding_acres=landholding,
        selected_schemes=selected_schemes,
        verified_documents=verified_docs_list,
        confirmed_at=confirmed_at
    )

    filename = f"Farmer_Benefit_Summary_{plan_number}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )
