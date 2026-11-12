from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.api.deps import get_optional_user, get_current_user
from app.models import User, FarmerProfile, Consent
from app.schemas import FarmerProfileCreate, FarmerProfileResponse

router = APIRouter(prefix="/profiles", tags=["Farmer Profile & Consent"])

@router.post("", response_model=FarmerProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(
    req: FarmerProfileCreate,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    # If user is logged in and is_temporary is False, require/log explicit consent per PRD 14.2
    is_temp = req.is_temporary or (current_user is None)
    crops_str = ",".join(req.primary_crops) if req.primary_crops else None

    profile = FarmerProfile(
        user_id=current_user.id if current_user else None,
        is_temporary=is_temp,
        district=req.district,
        landholding_acres=req.landholding_acres,
        farmer_category=req.farmer_category,
        primary_crops=crops_str,
        social_category=req.social_category,
        irrigation_source=req.irrigation_source
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)

    if current_user and not is_temp:
        consent = Consent(
            user_id=current_user.id,
            purpose="PROFILE_STORAGE",
            consented=True,
            version="1.0"
        )
        db.add(consent)
        db.commit()

    return FarmerProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        district=profile.district,
        landholding_acres=profile.landholding_acres,
        farmer_category=profile.farmer_category,
        primary_crops=profile.primary_crops.split(",") if profile.primary_crops else [],
        social_category=profile.social_category,
        irrigation_source=profile.irrigation_source,
        is_temporary=profile.is_temporary,
        created_at=profile.created_at
    )

@router.get("/{profile_id}", response_model=FarmerProfileResponse)
def get_profile(
    profile_id: str,
    current_user: User = Depends(get_optional_user),
    db: Session = Depends(get_db)
):
    profile = db.query(FarmerProfile).filter(FarmerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    
    # Server-side ownership check
    if profile.user_id and (not current_user or profile.user_id != current_user.id):
        raise HTTPException(status_code=403, detail="Access forbidden: you do not own this profile.")

    return FarmerProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        district=profile.district,
        landholding_acres=profile.landholding_acres,
        farmer_category=profile.farmer_category,
        primary_crops=profile.primary_crops.split(",") if profile.primary_crops else [],
        social_category=profile.social_category,
        irrigation_source=profile.irrigation_source,
        is_temporary=profile.is_temporary,
        created_at=profile.created_at
    )

@router.delete("/{profile_id}", status_code=status.HTTP_200_OK)
def delete_profile(
    profile_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(FarmerProfile).filter(FarmerProfile.id == profile_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")
    
    if profile.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access forbidden: you cannot delete another farmer's profile.")

    db.delete(profile)
    db.commit()
    return {"message": "Farmer profile permanently deleted."}

