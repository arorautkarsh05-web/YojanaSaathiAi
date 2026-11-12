import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_optional_user
from app.models import User, ActionPlan, FarmerProfile
from app.schemas import ActionPlanCreate, ActionPlanResponse
from app.services.action_plan_service import generate_action_plan

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

    # If user is authenticated and has a saved profile, persist the plan
    if current_user and db_profile and not db_profile.is_temporary:
        plan_record = ActionPlan(
            plan_number=plan_response.plan_number,
            user_id=current_user.id,
            profile_id=db_profile.id,
            selected_schemes_json=json.dumps(req.selected_scheme_codes),
            results_summary_json=json.dumps([s.model_dump() for s in plan_response.selected_schemes]),
            checklist_items_json=json.dumps([c.model_dump() for c in plan_response.checklist_items])
        )
        db.add(plan_record)
        db.commit()

    return plan_response

@router.get("/{plan_number}", response_model=ActionPlanResponse)
def get_action_plan_by_number(
    plan_number: str,
    db: Session = Depends(get_db)
):
    record = db.query(ActionPlan).filter(ActionPlan.plan_number == plan_number).first()
    if not record:
        raise HTTPException(status_code=404, detail="Action plan reference not found.")

    selected_schemes_raw = json.loads(record.results_summary_json)
    checklist_items_raw = json.loads(record.checklist_items_json)
    selected_codes = json.loads(record.selected_schemes_json)
    
    # Re-evaluate convergence for freshness
    from app.services.convergence_engine import check_multi_scheme_convergence
    convergence_results = check_multi_scheme_convergence(selected_codes)

    return ActionPlanResponse(
        plan_number=record.plan_number,
        created_at=record.created_at.isoformat(),
        selected_schemes=selected_schemes_raw,
        convergence_summary=convergence_results,
        checklist_items=checklist_items_raw,
        official_steps=[],
        disclaimer="योजना साथी एक स्वतंत्र सार्वजनिक मार्गदर्शक प्रणाली है। यह सीधे सरकारी आवेदन प्रस्तुत नहीं करती है। सभी आवेदन संबंधित आधिकारिक सरकारी पोर्टल या जन सुविधा केंद्र (CSC) के माध्यम से किए जाते हैं।"
    )

