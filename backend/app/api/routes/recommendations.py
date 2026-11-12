import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_optional_user
from app.models import User, FarmerProfile
from app.schemas import RecommendationRequest, RecommendationResponse
from app.services.eligibility_engine import evaluate_all_schemes

router = APIRouter(prefix="/recommendations", tags=["Eligibility & Discovery"])

@router.post("", response_model=RecommendationResponse)
def get_recommendations(
    req: RecommendationRequest,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    profile_dict = {}

    # If profile_id is provided, fetch from DB ensuring ownership if user is authenticated
    if req.profile_id:
        p = db.query(FarmerProfile).filter(FarmerProfile.id == req.profile_id).first()
        if p:
            if p.user_id and (not current_user or p.user_id != current_user.id):
                raise HTTPException(status_code=403, detail="Unauthorized access to this farmer profile.")
            profile_dict = {
                "district": p.district,
                "landholding_acres": p.landholding_acres,
                "farmer_category": p.farmer_category,
                "primary_crops": p.primary_crops.split(",") if p.primary_crops else [],
                "social_category": p.social_category,
                "irrigation_source": p.irrigation_source,
                "state": "Uttar Pradesh"
            }
    elif req.profile:
        profile_dict = req.profile.model_dump()
        profile_dict["state"] = "Uttar Pradesh"

    evaluated = evaluate_all_schemes(profile_dict, req.stated_needs)
    run_id = f"run_{uuid.uuid4().hex[:10]}"

    return RecommendationResponse(
        run_id=run_id,
        schemes=evaluated,
        generated_at=datetime.now(timezone.utc).isoformat(),
        total_schemes_evaluated=len(evaluated)
    )

