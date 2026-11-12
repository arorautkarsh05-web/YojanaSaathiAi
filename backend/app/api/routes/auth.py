from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from sqlalchemy.orm import Session
from typing import Optional
from app.db.session import get_db
from app.api.deps import get_current_user
from app.core.config import settings
from app.models import User
from app.schemas import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from app.services.auth_service import (
    register_user,
    authenticate_user,
    rotate_refresh_token,
    revoke_session,
    revoke_all_user_sessions
)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    user = register_user(db, req)
    roles = [r.role for r in user.roles]
    return UserResponse(
        id=user.id,
        email=user.email_normalized,
        display_name=user.display_name,
        roles=roles,
        account_status=user.account_status,
        created_at=user.created_at
    )

@router.post("/login", response_model=TokenResponse)
def login(
    req: UserLoginRequest,
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    user_agent = request.headers.get("user-agent")
    token_resp, raw_refresh = authenticate_user(db, req, user_agent=user_agent)
    
    # Set Secure HttpOnly cookie for refresh token
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=raw_refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/v1/auth"
    )
    return token_resp

@router.post("/refresh", response_model=TokenResponse)
def refresh(
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    raw_refresh = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if not raw_refresh:
        # Check header fallback for testing environments
        raw_refresh = request.headers.get("X-Refresh-Token")

    if not raw_refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cookie or header missing."
        )

    user_agent = request.headers.get("user-agent")
    token_resp, new_raw_refresh = rotate_refresh_token(db, raw_refresh, user_agent=user_agent)

    # Set new rotating refresh cookie
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=new_raw_refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
        path="/api/v1/auth"
    )
    return token_resp

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
    request: Request,
    db: Session = Depends(get_db)
):
    raw_refresh = request.cookies.get(settings.REFRESH_COOKIE_NAME)
    if raw_refresh:
        revoke_session(db, raw_refresh)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/api/v1/auth")
    return {"message": "Session successfully revoked."}

@router.post("/logout-all", status_code=status.HTTP_200_OK)
def logout_all(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    revoke_all_user_sessions(db, current_user.id)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/api/v1/auth")
    return {"message": "All user sessions have been revoked."}

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    roles = [r.role for r in current_user.roles]
    return UserResponse(
        id=current_user.id,
        email=current_user.email_normalized,
        display_name=current_user.display_name,
        roles=roles,
        account_status=current_user.account_status,
        created_at=current_user.created_at
    )

# --- DPDP Act 2023 Citizen Rights Endpoints ---

@router.post("/consent/withdraw", status_code=status.HTTP_200_OK)
def withdraw_consent(
    purpose: str = "PROFILE_STORAGE_AND_TERMS",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.services.auth_service import withdraw_user_consent
    consent = withdraw_user_consent(db, current_user.id, purpose)
    return {
        "status": "REVOKED",
        "purpose": consent.purpose,
        "revoked_at": consent.revoked_at.isoformat() if consent.revoked_at else None,
        "message": "Consent successfully withdrawn under DPDP Act 2023."
    }

@router.get("/export-data", status_code=status.HTTP_200_OK)
def export_my_data(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.services.auth_service import export_farmer_data
    return export_farmer_data(db, current_user.id)

@router.delete("/delete-account", status_code=status.HTTP_200_OK)
def delete_my_account(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.services.auth_service import delete_farmer_account
    delete_farmer_account(db, current_user.id)
    response.delete_cookie(settings.REFRESH_COOKIE_NAME, path="/api/v1/auth")
    return {
        "status": "PURGED",
        "message": "Farmer account and all personal profile records permanently erased under DPDP Right to Erasure."
    }

# --- Email Verification & Password Reset Endpoints ---

@router.post("/verify-email", status_code=status.HTTP_200_OK)
def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    from app.services.auth_service import verify_email_token
    user = verify_email_token(db, token)
    return {
        "status": "VERIFIED",
        "email": user.email_normalized,
        "verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
        "message": "Email address successfully verified."
    }

@router.post("/forgot-password", status_code=status.HTTP_200_OK)
def forgot_password(
    email: str,
    db: Session = Depends(get_db)
):
    from app.services.auth_service import normalize_email, generate_password_reset_token
    norm_email = normalize_email(email)
    user = db.query(User).filter(User.email_normalized == norm_email).first()
    reset_token = generate_password_reset_token(norm_email) if user else None
    resp = {
        "message": "If an account with this email exists, a password reset link has been dispatched."
    }
    if settings.DEBUG and reset_token:
        resp["debug_reset_token"] = reset_token
    return resp

@router.post("/reset-password", status_code=status.HTTP_200_OK)
def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db)
):
    from app.services.auth_service import reset_password_with_token
    reset_password_with_token(db, token, new_password)
    return {
        "message": "Password successfully reset. All previous sessions have been revoked. Please log in with your new password."
    }

