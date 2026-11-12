"""
Farmer Benefit Action Plan Service.
Generates a structured, evidence-backed preparation roadmap with deduplicated document checklists
and official application destinations.
"""

import uuid
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.services.scheme_catalogue import SCHEME_CATALOGUE
from app.services.eligibility_engine import evaluate_scheme
from app.services.convergence_engine import check_multi_scheme_convergence
from app.schemas import ActionPlanResponse, ChecklistItem, OfficialStep

def generate_action_plan(
    profile_data: Dict[str, Any],
    selected_scheme_codes: List[str],
    checklist_states: Optional[Dict[str, bool]] = None
) -> ActionPlanResponse:
    if checklist_states is None:
        checklist_states = {}

    evaluated_profile = profile_data.copy()
    if "state" not in evaluated_profile:
        evaluated_profile["state"] = "Uttar Pradesh"

    # Evaluate each selected scheme
    evaluated_schemes = []
    collected_docs_map = {}
    collected_steps = []
    step_num = 1

    for code in selected_scheme_codes:
        if code in SCHEME_CATALOGUE:
            scheme_meta = SCHEME_CATALOGUE[code]
            evaluation = evaluate_scheme(code, evaluated_profile)
            evaluated_schemes.append(evaluation)

            # Collect & deduplicate required documents
            for doc in scheme_meta.get("documents", []):
                doc_id = doc["id"]
                if doc_id not in collected_docs_map:
                    collected_docs_map[doc_id] = {
                        "id": doc_id,
                        "title_en": doc["title_en"],
                        "title_hi": doc["title_hi"],
                        "required_for_schemes": [code],
                        "is_ready": checklist_states.get(doc_id, False),
                        "source_authority": doc.get("source", "Official Department")
                    }
                else:
                    if code not in collected_docs_map[doc_id]["required_for_schemes"]:
                        collected_docs_map[doc_id]["required_for_schemes"].append(code)

            # Collect official next steps
            for step in scheme_meta.get("official_steps", []):
                collected_steps.append(
                    OfficialStep(
                        step_number=step_num,
                        title_en=f"[{code}] {step['title_en']}",
                        title_hi=f"[{code}] {step['title_hi']}",
                        description_en=step["description_en"],
                        description_hi=step["description_hi"],
                        portal_or_destination=step["portal_or_destination"],
                        is_independent=step.get("is_independent", True)
                    )
                )
                step_num += 1

    # Check pairwise convergence
    convergence_results = check_multi_scheme_convergence(selected_scheme_codes)

    # Format checklist items
    checklist_items = [
        ChecklistItem(
            id=d["id"],
            title_en=d["title_en"],
            title_hi=d["title_hi"],
            required_for_schemes=d["required_for_schemes"],
            is_ready=d["is_ready"],
            source_authority=d["source_authority"]
        )
        for d in collected_docs_map.values()
    ]

    plan_ref = f"YS-UP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
    now_iso = datetime.now(timezone.utc).isoformat()

    return ActionPlanResponse(
        plan_number=plan_ref,
        created_at=now_iso,
        selected_schemes=evaluated_schemes,
        convergence_summary=convergence_results,
        checklist_items=checklist_items,
        official_steps=collected_steps,
        disclaimer="योजना साथी एक स्वतंत्र सार्वजनिक मार्गदर्शक प्रणाली है। यह सीधे सरकारी आवेदन प्रस्तुत नहीं करती है। सभी आवेदन संबंधित आधिकारिक सरकारी पोर्टल या जन सुविधा केंद्र (CSC) के माध्यम से किए जाते हैं, और अंतिम पात्रता निर्धारण सक्षम सरकारी प्राधिकारी (जैसे तहसीलदार या जिला कृषि अधिकारी) द्वारा किया जाता है।"
    )

