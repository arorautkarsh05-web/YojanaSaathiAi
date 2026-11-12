"""
YojanaSaathi AI — Farmer Benefit Readiness Engine.
Calculates objective, transparent preparation readiness progress for official application channels.
These are INTERNAL PREPARATION READINESS states, NOT government approvals or probabilistic guarantees.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

READINESS_STATES = {
    "READY_FOR_OFFICIAL_APPLICATION_REVIEW": {
        "title_en": "Ready for Official Application Review",
        "title_hi": "आधिकारिक आवेदन समीक्षा हेतु तैयार",
        "description_en": "All statutory mandatory eligibility conditions are passed, required documents are ready, and pairwise compatibility is confirmed.",
        "description_hi": "सभी अनिवार्य पात्रता शर्तें उत्तीर्ण हैं, आवश्यक दस्तावेज़ तैयार हैं और बहु-योजना सह-अस्तित्व सत्यापित है।"
    },
    "NEEDS_MORE_INFORMATION": {
        "title_en": "Needs More Information",
        "title_hi": "अतिरिक्त जानकारी आवश्यक",
        "description_en": "One or more mandatory attributes (e.g. landholding, water source, or crops) remain unspecified or unverified.",
        "description_hi": "एक या अधिक अनिवार्य जानकारी (जैसे भूमि रकबा, जल स्रोत, या फसल) अपूर्ण अथवा असत्यापित है।"
    },
    "DOCUMENTS_PENDING": {
        "title_en": "Required Documents Pending",
        "title_hi": "दस्तावेज़ तैयारी शेष",
        "description_en": "Farmer satisfies eligibility criteria, but one or more mandatory documents (e.g. Khatauni, Sowing Certificate) are not yet in hand.",
        "description_hi": "पात्रता पूर्ण है परंतु आवश्यक दस्तावेज़ (जैसे खतौनी नकल, बुवाई प्रमाण पत्र) अभी तैयार नहीं हैं।"
    },
    "POLICY_VERIFICATION_REQUIRED": {
        "title_en": "Policy / Cluster Verification Required",
        "title_hi": "विभागीय विज्ञप्ति / क्लस्टर सत्यापन आवश्यक",
        "description_en": "Scheme depends on open departmental notification windows (token booking) or seasonal district crop cluster notices.",
        "description_hi": "योजना विभागीय टोकन बुकिंग विज्ञप्ति अथवा मौसमी जिला क्लस्टर अधिसूचना के सत्यापन पर निर्भर है।"
    },
    "NOT_ELIGIBLE": {
        "title_en": "Not Eligible under Current Statutory Rules",
        "title_hi": "वर्तमान नियमों के अनुसार अपात्र",
        "description_en": "One or more mandatory statutory exclusion criteria (e.g. non-notified crops, institutional landholder, land ceiling) are failed.",
        "description_hi": "एक या अधिक अनिवार्य पात्रता शर्तें (जैसे गैर-अधिसूचित फसल, संस्थागत भू-धारक) पूरी नहीं होती हैं।"
    },
    "SCHEME_DATA_OUTDATED": {
        "title_en": "Scheme Source Data Outdated",
        "title_hi": "योजना स्रोत डेटा पुनरावलोकन प्रतीक्षित",
        "description_en": "Scheme guidelines have expired or are undergoing active legislative review.",
        "description_hi": "योजना दिशानिर्देशों की वैधता अवधि पूर्ण हो चुकी है अथवा विधायी संशोधन प्रक्रिया में है।"
    }
}

@dataclass
class SchemeReadinessOutcome:
    scheme_code: str
    readiness_state: str
    readiness_score_pct: float
    factors: Dict[str, Any]
    next_action_en: str
    next_action_hi: str

def evaluate_farmer_scheme_readiness(
    scheme_code: str,
    overall_status: str,
    unknown_rule_count: int,
    failed_rule_count: int,
    total_docs_count: int,
    ready_docs_count: int,
    geo_applicability: str,
    verification_status: str
) -> SchemeReadinessOutcome:
    """
    Computes transparent preparation readiness score and state.
    Formula:
    Readiness Score = (0.50 * EligibilityCompleteness) + (0.30 * DocumentPreparation) + (0.20 * AdministrativeCertainty)
    """
    # 1. Eligibility Completeness (0 to 100)
    if overall_status == "LIKELY_NOT_ELIGIBLE" or failed_rule_count > 0:
        elig_score = 0.0
    elif overall_status == "NEEDS_MORE_INFO" or unknown_rule_count > 0:
        elig_score = 40.0
    else:
        elig_score = 100.0

    # 2. Document Preparation (0 to 100)
    doc_ratio = (ready_docs_count / max(total_docs_count, 1)) if total_docs_count > 0 else 1.0
    doc_score = round(doc_ratio * 100.0, 1)

    # 3. Administrative / Spatial Certainty (0 to 100)
    if geo_applicability == "NOT_APPLICABLE":
        admin_score = 0.0
    elif geo_applicability == "UNKNOWN_REQUIRES_VERIFICATION" or verification_status == "REQUIRES_REVIEW":
        admin_score = 60.0
    elif verification_status in ["OUTDATED", "SUPERSEDED"]:
        admin_score = 30.0
    else:
        admin_score = 100.0

    # Composite Readiness Score
    readiness_score = round(
        (0.50 * elig_score) +
        (0.30 * doc_score) +
        (0.20 * admin_score),
        1
    )

    # State Resolution
    if overall_status == "LIKELY_NOT_ELIGIBLE" or geo_applicability == "NOT_APPLICABLE":
        state = "NOT_ELIGIBLE"
        next_en = "Review ineligible criteria; explore alternate welfare schemes."
        next_hi = "अपात्रता कारणों की समीक्षा करें; वैकल्पिक सरकारी योजनाओं का अन्वेषण करें।"
    elif verification_status in ["OUTDATED", "SUPERSEDED"]:
        state = "SCHEME_DATA_OUTDATED"
        next_en = "Wait for updated state government order publication."
        next_hi = "अद्यतन सरकारी शासनादेश प्रकाशन की प्रतीक्षा करें।"
    elif unknown_rule_count > 0 or overall_status == "NEEDS_MORE_INFO":
        state = "NEEDS_MORE_INFORMATION"
        next_en = "Provide missing profile attributes (land record, irrigation source, crop)."
        next_hi = "अपूर्ण प्रोफ़ाइल विवरण (भूमि रकबा, जल स्रोत, फसल) दर्ज करें।"
    elif geo_applicability == "UNKNOWN_REQUIRES_VERIFICATION" or verification_status == "REQUIRES_REVIEW":
        state = "POLICY_VERIFICATION_REQUIRED"
        next_en = "Confirm current seasonal crop notification with District Agriculture Officer."
        next_hi = "जिला कृषि अधिकारी कार्यालय से वर्तमान मौसमी फसल अधिसूचना की पुष्टि करें।"
    elif total_docs_count > 0 and ready_docs_count < total_docs_count:
        state = "DOCUMENTS_PENDING"
        next_en = f"Procure remaining {total_docs_count - ready_docs_count} pending documents from Tehsil or Bank."
        next_hi = f"तहसील या बैंक से शेष {total_docs_count - ready_docs_count} दस्तावेज़ प्राप्त करें।"
    else:
        state = "READY_FOR_OFFICIAL_APPLICATION_REVIEW"
        next_en = "Proceed to official portal or CSC with verified document checklist."
        next_hi = "सत्यापित दस्तावेज़ चेकलिस्ट के साथ आधिकारिक पोर्टल अथवा सीएससी पर आवेदन करें।"

    return SchemeReadinessOutcome(
        scheme_code=scheme_code,
        readiness_state=state,
        readiness_score_pct=readiness_score,
        factors={
            "eligibility_completeness": elig_score,
            "document_preparation_pct": doc_score,
            "administrative_certainty": admin_score,
            "weights": "50% Eligibility, 30% Documents, 20% Administrative Certainty"
        },
        next_action_en=next_en,
        next_action_hi=next_hi
    )

