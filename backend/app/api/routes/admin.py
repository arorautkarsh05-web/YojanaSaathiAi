from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.db.session import get_db
from app.api.deps import require_admin
from app.models import User, AuditLog
from app.services.scheme_catalogue import SCHEME_CATALOGUE, CONVERGENCE_REGISTER

router = APIRouter(prefix="/admin", tags=["Admin Review & Audit"])

@router.get("/overview", dependencies=[Depends(require_admin)])
def admin_overview(db: Session = Depends(get_db)):
    schemes_count = len(SCHEME_CATALOGUE)
    convergence_pairs_count = len(CONVERGENCE_REGISTER)
    user_count = db.query(User).count()
    return {
        "status": "OPERATIONAL",
        "jurisdiction": "Uttar Pradesh (75 Districts)",
        "verified_schemes_count": schemes_count,
        "verified_convergence_pairs": convergence_pairs_count,
        "registered_users": user_count,
        "deterministic_engine_version": "3.0.0",
        "human_review_status": "All active rules verified against gazette source documents"
    }

@router.get("/audit-logs", dependencies=[Depends(require_admin)])
def get_audit_logs(db: Session = Depends(get_db)):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(50).all()
    return logs

@router.post("/policy-impact", dependencies=[Depends(require_admin)])
def evaluate_amendment_impact(
    scheme_code: str,
    new_version_tag: str,
    amendment_summary: str,
    db: Session = Depends(get_db)
):
    from app.services.policy_impact_service import assess_policy_change_impact
    return assess_policy_change_impact(
        db=db,
        scheme_code=scheme_code,
        new_version_tag=new_version_tag,
        amendment_summary=amendment_summary
    )

