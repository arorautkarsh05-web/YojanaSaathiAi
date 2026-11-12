"""
Authentication & Authorization Service.
Handles registration, Argon2id password verification, JWT access tokens, rotating opaque refresh tokens,
and server-side RBAC.
"""

import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.core.config import settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    generate_opaque_token,
    hash_token
)
from app.models import User, UserRole, AuthSession, AuditLog, Consent, FarmerProfile, ActionPlan, generate_uuid
import jwt
from app.schemas import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse

# In-memory sliding-window rate limiter
_rate_limit_records = defaultdict(list)

def check_rate_limit(key: str, max_requests: int, window_seconds: int = 60) -> bool:
    """Sliding-window rate limiter preventing brute-force and credential stuffing."""
    now = time.time()
    valid_timestamps = [t for t in _rate_limit_records[key] if now - t < window_seconds]
    if len(valid_timestamps) >= max_requests:
        return False
    valid_timestamps.append(now)
    _rate_limit_records[key] = valid_timestamps
    return True

def normalize_email(email: str) -> str:
    return email.strip().lower()

def register_user(db: Session, req: UserRegisterRequest, ip_address: Optional[str] = None) -> User:
    norm_email = normalize_email(req.email)
    
    # Rate limit registration per IP / email
    rate_key = f"reg_{ip_address or norm_email}"
    if not check_rate_limit(rate_key, settings.RATE_LIMIT_REGISTER_PER_HOUR, 3600):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Registration rate limit exceeded. Please try again later."
        )

    existing = db.query(User).filter(User.email_normalized == norm_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    hashed_pw = hash_password(req.password)
    email_verified = None if settings.REQUIRE_EMAIL_VERIFICATION else datetime.now(timezone.utc)
    
    user = User(
        email_normalized=norm_email,
        display_name=req.display_name,
        password_hash=hashed_pw,
        account_status="ACTIVE",
        email_verified_at=email_verified
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Assign default FARMER role
    farmer_role = UserRole(
        user_id=user.id,
        role="FARMER",
        granted_by="SYSTEM"
    )
    db.add(farmer_role)

    # Record terms consent
    if req.terms_consented:
        consent = Consent(
            user_id=user.id,
            purpose="PROFILE_STORAGE_AND_TERMS",
            consent_version="3.0",
            status="ACTIVE",
            granted_at=datetime.now(timezone.utc),
            ip_hash=hash_token(ip_address) if ip_address else None
        )
        db.add(consent)

    audit = AuditLog(
        user_id=user.id,
        action="USER_REGISTRATION",
        resource_type="USER",
        resource_id=user.id,
        metadata_json=f'{{"email": "{norm_email}"}}',
        created_at=datetime.now(timezone.utc)
    )
    db.add(audit)
    db.commit()
    return user

def authenticate_user(db: Session, req: UserLoginRequest, user_agent: Optional[str] = None, ip_address: Optional[str] = None) -> Tuple[TokenResponse, str]:
    norm_email = normalize_email(req.email)

    # Rate limiting on login attempts
    rate_key = f"login_{ip_address or norm_email}"
    if not check_rate_limit(rate_key, settings.RATE_LIMIT_LOGIN_PER_MINUTE, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait 1 minute before trying again."
        )

    user = db.query(User).filter(User.email_normalized == norm_email).first()
    if not user or not verify_password(req.password, user.password_hash):
        # Security event log for failed login attempt
        audit = AuditLog(
            user_id=user.id if user else None,
            action="LOGIN_FAILED",
            resource_type="USER",
            resource_id=norm_email,
            metadata_json='{"reason": "Invalid credentials"}',
            created_at=datetime.now(timezone.utc)
        )
        db.add(audit)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    if user.account_status != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account is {user.account_status}."
        )

    if settings.REQUIRE_EMAIL_VERIFICATION and user.email_verified_at is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email address has not been verified. Please verify your email first."
        )

    # Update last login
    now = datetime.now(timezone.utc)
    user.last_login_at = now

    # Create access token
    roles = [r.role for r in user.roles]
    token_payload = {
        "sub": user.id,
        "email": user.email_normalized,
        "roles": roles
    }
    access_token = create_access_token(token_payload)

    # Generate rotating opaque refresh token with unique session family ID
    raw_refresh = generate_opaque_token()
    refresh_hash = hash_token(raw_refresh)
    expires_at = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    family_id = generate_uuid()

    session = AuthSession(
        user_id=user.id,
        family_id=family_id,
        refresh_token_hash=refresh_hash,
        expires_at=expires_at,
        user_agent_summary=user_agent[:250] if user_agent else None
    )
    db.add(session)

    audit = AuditLog(
        user_id=user.id,
        action="LOGIN_SUCCESS",
        resource_type="AUTH_SESSION",
        resource_id=session.id,
        metadata_json=f'{{"family_id": "{family_id}"}}',
        created_at=now
    )
    db.add(audit)
    db.commit()

    user_resp = UserResponse(
        id=user.id,
        email=user.email_normalized,
        display_name=user.display_name,
        roles=roles,
        account_status=user.account_status,
        created_at=user.created_at
    )

    token_resp = TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_resp
    )
    return token_resp, raw_refresh

def rotate_refresh_token(db: Session, raw_token: str, user_agent: Optional[str] = None) -> Tuple[TokenResponse, str]:
    """
    Rotates refresh token. Detects reuse attacks and revokes entire session family.
    """
    token_hash = hash_token(raw_token)
    session = db.query(AuthSession).filter(AuthSession.refresh_token_hash == token_hash).first()
    now = datetime.now(timezone.utc)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh session."
        )

    # Replay Attack Detection: If session was ALREADY revoked, an attacker is reusing a stolen token!
    if session.revoked_at is not None:
        # Revoke the entire session family for this user
        target_family = session.family_id or session.id
        db.query(AuthSession).filter(
            (AuthSession.family_id == target_family) | (AuthSession.user_id == session.user_id)
        ).update({AuthSession.revoked_at: now}, synchronize_session=False)

        audit = AuditLog(
            user_id=session.user_id,
            action="SECURITY_ALERT_REFRESH_TOKEN_REPLAY",
            resource_type="AUTH_SESSION",
            resource_id=session.id,
            metadata_json=f'{{"alert": "Token replay detected for family {target_family}. All sessions revoked."}}',
            created_at=now
        )
        db.add(audit)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Security violation: Token replay detected. All active sessions have been revoked."
        )

    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired."
        )

    # Revoke current session on rotation
    session.revoked_at = now
    
    user = session.user
    if not user or user.account_status != "ACTIVE":
        db.commit()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is inactive.")

    # Create new refresh session preserving the family ID
    new_raw_refresh = generate_opaque_token()
    new_refresh_hash = hash_token(new_raw_refresh)
    new_session = AuthSession(
        user_id=user.id,
        family_id=session.family_id or session.id,
        refresh_token_hash=new_refresh_hash,
        expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        rotated_from_session_id=session.id,
        user_agent_summary=user_agent[:250] if user_agent else None
    )
    db.add(new_session)
    db.commit()

    roles = [r.role for r in user.roles]
    token_payload = {
        "sub": user.id,
        "email": user.email_normalized,
        "roles": roles
    }
    new_access_token = create_access_token(token_payload)

    user_resp = UserResponse(
        id=user.id,
        email=user.email_normalized,
        display_name=user.display_name,
        roles=roles,
        account_status=user.account_status,
        created_at=user.created_at
    )

    token_resp = TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_resp
    )
    return token_resp, new_raw_refresh

def revoke_session(db: Session, raw_token: str):
    """Revokes a single session."""
    token_hash = hash_token(raw_token)
    session = db.query(AuthSession).filter(AuthSession.refresh_token_hash == token_hash).first()
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()

def revoke_all_user_sessions(db: Session, user_id: str):
    """Revokes all active sessions for a user."""
    now = datetime.now(timezone.utc)
    sessions = db.query(AuthSession).filter(
        AuthSession.user_id == user_id,
        AuthSession.revoked_at.is_(None)
    ).all()
    for s in sessions:
        s.revoked_at = now
    db.commit()

# --- DPDP Act 2023 Citizen Rights & Privacy Operations ---

def withdraw_user_consent(db: Session, user_id: str, purpose: str = "PROFILE_STORAGE_AND_TERMS") -> Consent:
    """Withdraws consent per Section 6(4) of the DPDP Act 2023."""
    consent = db.query(Consent).filter(
        Consent.user_id == user_id,
        Consent.purpose == purpose,
        Consent.status == "ACTIVE"
    ).first()
    now = datetime.now(timezone.utc)
    if consent:
        consent.status = "REVOKED"
        consent.revoked_at = now
    else:
        consent = Consent(
            user_id=user_id,
            purpose=purpose,
            consent_version="3.0",
            status="REVOKED",
            revoked_at=now
        )
        db.add(consent)

    audit = AuditLog(
        user_id=user_id,
        action="CONSENT_REVOCATION_DPDP",
        resource_type="CONSENT",
        resource_id=consent.id,
        metadata_json=f'{{"purpose": "{purpose}", "withdrawn_at": "{now.isoformat()}"}}',
        created_at=now
    )
    db.add(audit)
    db.commit()
    db.refresh(consent)
    return consent

def export_farmer_data(db: Session, user_id: str) -> dict:
    """Generates an export of all personal data held for the farmer (Right to Data Portability)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    profiles = db.query(FarmerProfile).filter(FarmerProfile.user_id == user_id).all()
    consents = db.query(Consent).filter(Consent.user_id == user_id).all()
    plans = db.query(ActionPlan).filter(ActionPlan.user_id == user_id).all()

    return {
        "export_metadata": {
            "requested_at": datetime.now(timezone.utc).isoformat(),
            "data_fiduciary": "YojanaSaathi AI — State of Uttar Pradesh",
            "statutory_basis": "Digital Personal Data Protection Act (DPDP) 2023 — Right to Data Portability",
            "format_version": "3.0"
        },
        "user_account": {
            "id": user.id,
            "email": user.email_normalized,
            "display_name": user.display_name,
            "account_status": user.account_status,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None
        },
        "farmer_profiles": [
            {
                "id": p.id,
                "district": p.district,
                "landholding_acres": p.landholding_acres,
                "primary_crops": p.primary_crops_json,
                "irrigation_source": p.irrigation_source,
                "created_at": p.created_at.isoformat() if p.created_at else None
            } for p in profiles
        ],
        "consents": [
            {
                "purpose": c.purpose,
                "version": c.consent_version,
                "status": c.status,
                "granted_at": c.granted_at.isoformat() if c.granted_at else None,
                "revoked_at": c.revoked_at.isoformat() if c.revoked_at else None
            } for c in consents
        ],
        "saved_action_plans": [
            {
                "plan_number": pl.plan_number,
                "selected_schemes": pl.selected_schemes_json,
                "created_at": pl.created_at.isoformat() if pl.created_at else None
            } for pl in plans
        ]
    }

def delete_farmer_account(db: Session, user_id: str) -> bool:
    """Permanently erases farmer profile, active sessions, and personal data (DPDP Right to Erasure)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    now = datetime.now(timezone.utc)
    # Record irreversible erasure audit event
    audit = AuditLog(
        user_id=user_id,
        action="USER_ACCOUNT_PURGED_DPDP_RIGHT_TO_ERASURE",
        resource_type="USER",
        resource_id=user_id,
        metadata_json='{"status": "PERMANENTLY_PURGED"}',
        created_at=now
    )
    db.add(audit)
    
    # Revoke all sessions first
    revoke_all_user_sessions(db, user_id)
    
    # Delete the user; cascading foreign keys will purge profiles, sessions, consents
    db.delete(user)
    db.commit()
    return True

# --- Verification & Password Reset Helpers ---

def generate_email_verification_token(email: str) -> str:
    payload = {
        "email": email,
        "type": "email_verification",
        "exp": (datetime.now(timezone.utc) + timedelta(hours=24)).timestamp()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def verify_email_token(db: Session, token: str) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "email_verification":
            raise HTTPException(status_code=400, detail="Invalid token type.")
        email = payload.get("email")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired email verification token.")

    user = db.query(User).filter(User.email_normalized == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    user.email_verified_at = datetime.now(timezone.utc)
    db.commit()
    return user

def generate_password_reset_token(email: str) -> str:
    payload = {
        "email": email,
        "type": "password_reset",
        "exp": (datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def reset_password_with_token(db: Session, token: str, new_password: str) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        if payload.get("type") != "password_reset":
            raise HTTPException(status_code=400, detail="Invalid token type.")
        email = payload.get("email")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or expired password reset token.")

    user = db.query(User).filter(User.email_normalized == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User account not found.")

    user.password_hash = hash_password(new_password)
    # Revoke all existing sessions on password change
    revoke_all_user_sessions(db, user.id)
    db.commit()
    return user

