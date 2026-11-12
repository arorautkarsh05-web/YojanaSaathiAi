import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, ForeignKey, Text, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.db.session import Base

def generate_uuid() -> str:
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    email_normalized = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(100), nullable=True)
    password_hash = Column(String(255), nullable=False)
    email_verified_at = Column(DateTime, nullable=True)
    account_status = Column(String(50), default="ACTIVE", nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = Column(DateTime, nullable=True)
    
    roles = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("AuthSession", back_populates="user", cascade="all, delete-orphan")
    profiles = relationship("FarmerProfile", back_populates="user")
    plans = relationship("ActionPlan", back_populates="user")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(50), nullable=False) # GUEST, FARMER, FACILITATOR, CONTENT_REVIEWER, ADMIN, SUPER_ADMIN
    granted_by = Column(String(100), nullable=True)
    granted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="roles")
    __table_args__ = (UniqueConstraint("user_id", "role", name="uq_user_role"),)

class AuthSession(Base):
    __tablename__ = "auth_sessions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    family_id = Column(String(36), nullable=False, default=generate_uuid, index=True)
    refresh_token_hash = Column(String(64), index=True, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    rotated_from_session_id = Column(String(36), nullable=True)
    user_agent_summary = Column(String(255), nullable=True)
    last_used_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="sessions")

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    is_temporary = Column(Boolean, default=True) # False requires explicit consent
    district = Column(String(100), nullable=False)
    landholding_acres = Column(Float, nullable=True)
    farmer_category = Column(String(50), nullable=True) # MARGINAL, SMALL, MEDIUM_LARGE
    primary_crops = Column(Text, nullable=True) # JSON array or comma separated
    social_category = Column(String(50), nullable=True) # GENERAL, OBC, SC_ST
    irrigation_source = Column(String(50), nullable=True) # TUBEWELL, CANAL, RAINFED, UNKNOWN
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="profiles")
    plans = relationship("ActionPlan", back_populates="profile")

class Consent(Base):
    __tablename__ = "consents"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True)
    purpose = Column(String(100), nullable=False) # PROFILE_STORAGE, ACTION_PLAN_PERSISTENCE, ASSISTED_MODE
    consent_version = Column(String(20), default="1.0", nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False) # ACTIVE, WITHDRAWN
    granted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    revoked_at = Column(DateTime, nullable=True)
    ip_hash = Column(String(64), nullable=True)
    user_agent_summary = Column(String(255), nullable=True)

class Scheme(Base):
    __tablename__ = "schemes"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scheme_code = Column(String(50), unique=True, index=True, nullable=False)
    official_name_en = Column(String(255), nullable=False)
    official_name_hi = Column(String(255), nullable=False)
    department = Column(String(255), nullable=False)
    level = Column(String(50), nullable=False) # CENTRAL, STATE_UP
    category = Column(String(100), default="AGRICULTURE_BENEFIT", nullable=False)
    benefit_type = Column(String(100), nullable=False) # DIRECT_BENEFIT_TRANSFER, SUBSIDY, INSURANCE, CREDIT
    benefit_summary_en = Column(Text, nullable=False)
    benefit_summary_hi = Column(Text, nullable=False)
    official_portal_url = Column(String(500), nullable=False)
    active_version_id = Column(String(36), nullable=True)
    
    versions = relationship("SchemeVersion", back_populates="scheme", cascade="all, delete-orphan")

class SchemeDocumentRequirement(Base):
    __tablename__ = "scheme_document_requirements"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scheme_code = Column(String(50), nullable=False, index=True)
    document_category = Column(String(100), nullable=False) # LAND_RECORD, IDENTITY_PROOF, BANK_PASSBOOK, RESIDENCE_PROOF, REGISTRATION_TOKEN, NO_DUES
    title_en = Column(String(255), nullable=False)
    title_hi = Column(String(255), nullable=False)
    issuing_authority = Column(String(255), nullable=False)
    accepted_formats = Column(String(100), default="PDF, Physical Original")
    is_mandatory = Column(Boolean, default=True)

class SchemeVersion(Base):
    __tablename__ = "scheme_versions"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scheme_id = Column(String(36), ForeignKey("schemes.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(String(20), default="1.0", nullable=False)
    status = Column(String(50), default="PUBLISHED", nullable=False) # DRAFT, IN_REVIEW, PUBLISHED, ARCHIVED
    verified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    verified_by = Column(String(100), nullable=False)
    source_title = Column(String(255), nullable=False)
    source_url = Column(String(500), nullable=False)
    source_section = Column(String(255), nullable=False)
    change_summary = Column(Text, nullable=True)
    
    scheme = relationship("Scheme", back_populates="versions")
    rules = relationship("EligibilityRule", back_populates="scheme_version", cascade="all, delete-orphan")

class EligibilityRule(Base):
    __tablename__ = "eligibility_rules"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scheme_version_id = Column(String(36), ForeignKey("scheme_versions.id", ondelete="CASCADE"), nullable=False)
    rule_code = Column(String(100), nullable=False)
    title_en = Column(String(255), nullable=False)
    title_hi = Column(String(255), nullable=False)
    field_name = Column(String(100), nullable=False)
    operator = Column(String(50), nullable=False) # GTE, LTE, EQUALS, IN, NOT_IN, BOOLEAN_TRUE
    target_value = Column(String(255), nullable=False)
    is_mandatory = Column(Boolean, default=True, nullable=False)
    source_citation = Column(String(500), nullable=False)
    
    scheme_version = relationship("SchemeVersion", back_populates="rules")

class CompatibilityRule(Base):
    __tablename__ = "compatibility_rules"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    scheme_code_a = Column(String(50), nullable=False, index=True)
    scheme_code_b = Column(String(50), nullable=False, index=True)
    status = Column(String(50), nullable=False) # COMPATIBLE_CONFIRMED, INCOMPATIBLE_CONFIRMED, UNKNOWN_REQUIRES_VERIFICATION
    evidence_text = Column(Text, nullable=False)
    authoritative_source = Column(String(500), nullable=False)
    source_section = Column(String(255), nullable=False)
    verified_by = Column(String(100), nullable=False)
    verified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class ActionPlan(Base):
    __tablename__ = "action_plans"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    plan_number = Column(String(50), unique=True, index=True, nullable=False)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    profile_id = Column(String(36), ForeignKey("farmer_profiles.id", ondelete="CASCADE"), nullable=False)
    selected_schemes_json = Column(Text, nullable=False) # JSON array of scheme codes
    results_summary_json = Column(Text, nullable=False) # JSON of scheme evaluation
    checklist_items_json = Column(Text, nullable=False) # JSON of readiness items
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = relationship("User", back_populates="plans")
    profile = relationship("FarmerProfile", back_populates="plans")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(100), nullable=True)
    metadata_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

