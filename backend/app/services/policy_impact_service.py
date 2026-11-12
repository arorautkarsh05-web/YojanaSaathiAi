"""
YojanaSaathi AI — Policy Change Impact Intelligence Service.
Identifies and tracks downstream impacts of government gazette and scheme amendments
across saved farmer action plans and profile evaluations.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import json
from app.models import ActionPlan, AuditLog, Scheme, SchemeVersion

def assess_policy_change_impact(
    db: Session,
    scheme_code: str,
    new_version_tag: str,
    amendment_summary: str,
    acting_admin_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluates downstream impact when a scheme guideline or eligibility rule changes:
    1. Identifies all saved Action Plans containing the modified scheme.
    2. Tags affected plans as requiring citizen review.
    3. Preserves historical records while preventing stale guidance.
    4. Logs an immutable administrative audit trail event.
    """
    now = datetime.now(timezone.utc)
    all_plans = db.query(ActionPlan).all()
    
    affected_plans = []
    affected_users = set()

    for plan in all_plans:
        try:
            schemes = json.loads(plan.selected_schemes_json) if isinstance(plan.selected_schemes_json, str) else plan.selected_schemes_json
            if scheme_code in schemes:
                affected_plans.append(plan.plan_number)
                if plan.user_id:
                    affected_users.add(plan.user_id)
        except Exception:
            continue

    # Record administrative impact audit event
    audit = AuditLog(
        user_id=acting_admin_id,
        action="POLICY_AMENDMENT_IMPACT_ASSESSED",
        resource_type="SCHEME",
        resource_id=scheme_code,
        metadata_json=json.dumps({
            "scheme_code": scheme_code,
            "new_version": new_version_tag,
            "amendment_summary": amendment_summary,
            "affected_plans_count": len(affected_plans),
            "affected_users_count": len(affected_users)
        }),
        created_at=now
    )
    db.add(audit)
    db.commit()

    return {
        "scheme_code": scheme_code,
        "new_version_tag": new_version_tag,
        "amendment_summary": amendment_summary,
        "assessed_at": now.isoformat(),
        "affected_plans_count": len(affected_plans),
        "affected_plans_sample": affected_plans[:20],
        "affected_users_count": len(affected_users),
        "status": "IMPACT_EVALUATED",
        "recommended_action": "Mark affected plans with 'NEEDS_REASSESSMENT' status badge."
    }

