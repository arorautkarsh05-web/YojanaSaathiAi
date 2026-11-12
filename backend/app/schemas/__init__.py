from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Auth Schemas ---
class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Minimum 8 characters")
    display_name: Optional[str] = None
    terms_consented: bool = Field(..., description="Must acknowledge terms and privacy notice")

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: str
    display_name: Optional[str] = None
    roles: List[str] = []
    account_status: str
    created_at: datetime

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

# --- Profile Schemas ---
class FarmerProfileCreate(BaseModel):
    district: str
    landholding_acres: Optional[float] = None
    farmer_category: Optional[str] = None # MARGINAL, SMALL, MEDIUM_LARGE
    primary_crops: Optional[List[str]] = []
    social_category: Optional[str] = None # GENERAL, OBC, SC_ST
    irrigation_source: Optional[str] = None # TUBEWELL, CANAL, RAINFED, UNKNOWN
    is_temporary: bool = True # Default True for guest / unconsented storage

class FarmerProfileResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    district: str
    landholding_acres: Optional[float] = None
    farmer_category: Optional[str] = None
    primary_crops: List[str] = []
    social_category: Optional[str] = None
    irrigation_source: Optional[str] = None
    is_temporary: bool
    created_at: datetime

# --- Eligibility & Rules Schemas ---
class RuleOutcome(BaseModel):
    rule_code: str
    title_en: str
    title_hi: str
    status: str # PASS, FAIL, UNKNOWN
    reason: str
    citation: str
    is_mandatory: bool

class SchemeEvaluation(BaseModel):
    scheme_code: str
    official_name_en: str
    official_name_hi: str
    department: str
    level: str # CENTRAL, STATE_UP
    category: Optional[str] = "AGRICULTURE_BENEFIT"
    benefit_type: str
    benefit_summary_en: str
    benefit_summary_hi: str
    overall_status: str # LIKELY_ELIGIBLE, NEEDS_MORE_INFO, LIKELY_NOT_ELIGIBLE
    passed_rules: List[RuleOutcome]
    failed_rules: List[RuleOutcome]
    unknown_rules: List[RuleOutcome]
    official_portal_url: str
    verified_at: str
    source_title: str
    source_section: str
    source_url: str
    ranking_score: Optional[float] = None
    ranking_factors: Optional[Dict[str, Any]] = None
    recommendation_reason: Optional[str] = None
    readiness_state: Optional[str] = None

class RecommendationRequest(BaseModel):
    stated_needs: List[str] = [] # e.g. ["crop_insurance", "irrigation", "income_support", "credit", "machinery", "social_security"]
    profile: Optional[FarmerProfileCreate] = None
    profile_id: Optional[str] = None

class RecommendationResponse(BaseModel):
    run_id: str
    schemes: List[SchemeEvaluation]
    generated_at: str
    total_schemes_evaluated: int
    ranking_strategy: Optional[str] = "Multi-Factor Need Weighted (40% Needs, 35% Eligibility, 10% Geography, 15% Freshness)"

# --- Convergence & Multi-Scheme Schemas ---
class PairwiseConvergence(BaseModel):
    scheme_code_a: str
    scheme_code_b: str
    status: str # COMPATIBLE_CONFIRMED, INCOMPATIBLE_CONFIRMED, UNKNOWN_REQUIRES_VERIFICATION
    evidence_text: str
    authoritative_source: str
    source_section: str
    verified_by: str
    verified_at: str

class ConvergenceCheckRequest(BaseModel):
    scheme_codes: List[str]

class ConvergenceCheckResponse(BaseModel):
    pairs: List[PairwiseConvergence]

class GraphNode(BaseModel):
    id: str
    label_en: str
    label_hi: str
    category: str
    department: str
    overall_status: Optional[str] = "UNKNOWN"

class GraphEdge(BaseModel):
    source: str
    target: str
    status: str # COMPATIBLE_CONFIRMED, INCOMPATIBLE_CONFIRMED, UNKNOWN_REQUIRES_VERIFICATION
    evidence_text: str
    authoritative_source: str
    source_section: str
    verified_by: str

class ConvergenceGraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

# --- Consent Schemas ---
class ConsentRecordRequest(BaseModel):
    purpose: str
    consent_version: str = "3.0"

class ConsentResponse(BaseModel):
    id: str
    purpose: str
    consent_version: str
    status: str
    granted_at: datetime
    revoked_at: Optional[datetime] = None

# --- Action Plan Schemas ---
class ChecklistItem(BaseModel):
    id: str
    title_en: str
    title_hi: str
    required_for_schemes: List[str]
    is_ready: bool = False
    source_authority: str

class OfficialStep(BaseModel):
    step_number: int
    title_en: str
    title_hi: str
    description_en: str
    description_hi: str
    portal_or_destination: str
    is_independent: bool = True

class ActionPlanCreate(BaseModel):
    profile_id: Optional[str] = None
    profile: Optional[FarmerProfileCreate] = None
    selected_scheme_codes: List[str]
    checklist_states: Optional[Dict[str, bool]] = {}

class ActionPlanResponse(BaseModel):
    plan_number: str
    created_at: str
    selected_schemes: List[SchemeEvaluation]
    convergence_summary: List[PairwiseConvergence]
    checklist_items: List[ChecklistItem]
    official_steps: List[OfficialStep]
    disclaimer: str

# --- Grounded Q&A Schemas ---
class AssistantQueryRequest(BaseModel):
    query: str
    scheme_code: Optional[str] = None
    language: Optional[str] = "hi"  # "hi", "en", "hinglish", "pa"

class AssistantQueryResponse(BaseModel):
    answer: str
    source_title: str
    authority: str
    section: str
    verified_at: str
    can_verify: bool
    detected_language: Optional[str] = "hi"
    related_schemes: Optional[List[str]] = []

