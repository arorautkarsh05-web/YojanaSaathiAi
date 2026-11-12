"""
Deterministic Three-Valued Rules Engine for YojanaSaathi AI.
Evaluates confirmed farmer profile attributes against statutory rules returning PASS, FAIL, or UNKNOWN.
The LLM does NOT make eligibility decisions; this engine is strictly deterministic and auditable.
"""

from typing import Dict, Any, List, Tuple, Optional
from app.services.scheme_catalogue import SCHEME_CATALOGUE
from app.services.geo_applicability import evaluate_geographic_applicability, normalize_district_name
from app.schemas import RuleOutcome, SchemeEvaluation

def parse_landholding_to_acres(val: Any, unit_hint: Optional[str] = None) -> Tuple[Optional[float], Optional[str]]:
    """
    Parses landholding into standard acres, supporting Bigha and Hectare conversions for UP.
    Returns (acres_float, error_string).
    Standard UP conversions:
    1 Pucca Bigha = 0.625 Acres (approx 5/8 acre).
    1 Hectare = 2.471 Acres.
    """
    if val is None:
        return None, None
    str_val = str(val).strip().lower()
    if not str_val:
        return None, None
    
    mult = 1.0
    hint_str = str(unit_hint or "").strip().lower()
    if "bigha" in str_val or "bigha" in hint_str:
        mult = 0.625
        str_val = str_val.replace("bigha", "").replace("बीघा", "").strip()
    elif "hectare" in str_val or "hektare" in str_val or "हेक्टेयर" in str_val or "hectare" in hint_str:
        mult = 2.471
        str_val = str_val.replace("hectare", "").replace("हेक्टेयर", "").strip()
    elif "acre" in str_val or "एकड़" in str_val:
        str_val = str_val.replace("acre", "").replace("एकड़", "").strip()

    try:
        num = float(str_val) * mult
        if num < 0:
            return None, f"Invalid physical quantity: landholding cannot be negative ({num:.2f} acres)."
        return round(num, 3), None
    except ValueError:
        return None, f"Could not parse numeric landholding from '{val}'."

def evaluate_single_rule(rule: Dict[str, Any], profile_data: Dict[str, Any]) -> RuleOutcome:
    """
    Evaluates one statutory rule against profile fields using 3-valued logic (PASS, FAIL, UNKNOWN).
    Never converts missing, ambiguous, or physically invalid fields to PASS.
    """
    field_name = rule["field_name"]
    operator = rule["operator"]
    target_value = rule["target_value"]
    is_mandatory = rule.get("is_mandatory", True)
    citation = rule["citation"]
    title_en = rule["title_en"]
    title_hi = rule["title_hi"]
    rule_code = rule["rule_code"]

    # Rule validity check: expired or superseded rules must never produce confirmed PASS
    if rule.get("is_active") is False or rule.get("status") in ["SUPERSEDED", "EXPIRED", "OUTDATED"]:
        return RuleOutcome(
            rule_code=rule_code,
            title_en=title_en,
            title_hi=title_hi,
            status="UNKNOWN",
            reason="Statutory rule is marked superseded or expired and requires administrative re-verification.",
            citation=citation,
            is_mandatory=is_mandatory
        )

    # If field is missing or explicitly None, return UNKNOWN
    if field_name not in profile_data or profile_data[field_name] is None:
        return RuleOutcome(
            rule_code=rule_code,
            title_en=title_en,
            title_hi=title_hi,
            status="UNKNOWN",
            reason=f"Profile is missing required data for '{field_name}'.",
            citation=citation,
            is_mandatory=is_mandatory
        )

    val = profile_data[field_name]

    # Empty string or empty collection check
    if isinstance(val, str) and not val.strip():
        return RuleOutcome(
            rule_code=rule_code,
            title_en=title_en,
            title_hi=title_hi,
            status="UNKNOWN",
            reason=f"Field '{field_name}' is blank or empty string.",
            citation=citation,
            is_mandatory=is_mandatory
        )

    if isinstance(val, list) and len(val) == 0:
        return RuleOutcome(
            rule_code=rule_code,
            title_en=title_en,
            title_hi=title_hi,
            status="UNKNOWN",
            reason=f"Field '{field_name}' has no selected entries; verification required.",
            citation=citation,
            is_mandatory=is_mandatory
        )

    # Landholding Unit and Boundary Validation
    if field_name == "landholding_acres":
        unit_hint = profile_data.get("land_unit") or profile_data.get("landholding_unit")
        parsed_acres, parse_err = parse_landholding_to_acres(val, unit_hint=unit_hint)
        if parse_err:
            return RuleOutcome(
                rule_code=rule_code,
                title_en=title_en,
                title_hi=title_hi,
                status="UNKNOWN",
                reason=parse_err,
                citation=citation,
                is_mandatory=is_mandatory
            )
        val = parsed_acres

    # Evaluate based on operator
    try:
        if operator == "GTE":
            num_val = float(val)
            target_num = float(target_value)
            if num_val >= target_num:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="PASS",
                    reason=f"Value ({num_val}) meets or exceeds statutory threshold ({target_num}).",
                    citation=citation,
                    is_mandatory=is_mandatory
                )
            else:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="FAIL",
                    reason=f"Value ({num_val}) is below statutory minimum requirement ({target_num}).",
                    citation=citation,
                    is_mandatory=is_mandatory
                )

        elif operator == "LTE":
            num_val = float(val)
            target_num = float(target_value)
            if num_val <= target_num:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="PASS",
                    reason=f"Value ({num_val}) is within maximum ceiling ({target_num}).",
                    citation=citation,
                    is_mandatory=is_mandatory
                )
            else:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="FAIL",
                    reason=f"Value ({num_val}) exceeds statutory maximum ({target_num}).",
                    citation=citation,
                    is_mandatory=is_mandatory
                )

        elif operator == "EQUALS":
            str_val = str(val).strip().lower()
            str_target = str(target_value).strip().lower()
            if str_val == str_target:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="PASS",
                    reason=f"Field matches statutory condition ('{val}').",
                    citation=citation,
                    is_mandatory=is_mandatory
                )
            else:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="FAIL",
                    reason=f"Field ('{val}') does not match required statutory value ('{target_value}').",
                    citation=citation,
                    is_mandatory=is_mandatory
                )

        elif operator == "IN":
            # Target value is list of allowed values
            allowed = [str(x).strip().lower() for x in target_value] if isinstance(target_value, list) else [str(target_value).strip().lower()]
            str_val = str(val).strip().lower()
            if str_val in allowed:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="PASS",
                    reason=f"Value ('{val}') is in the approved statutory category list.",
                    citation=citation,
                    is_mandatory=is_mandatory
                )
            else:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="FAIL",
                    reason=f"Value ('{val}') is not among eligible options.",
                    citation=citation,
                    is_mandatory=is_mandatory
                )

        elif operator == "INTERSECT_ANY":
            user_items = [str(x).strip().lower() for x in val] if isinstance(val, list) else [str(val).strip().lower()]
            user_items = [x for x in user_items if x]
            if not user_items:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="UNKNOWN",
                    reason="No crops specified in profile; seasonal crop verification required.",
                    citation=citation,
                    is_mandatory=is_mandatory
                )

            target_items = [str(x).strip().lower() for x in target_value] if isinstance(target_value, list) else [str(target_value).strip().lower()]
            matched = set(user_items).intersection(set(target_items))
            if matched:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="PASS",
                    reason=f"Cultivates notified crop(s): {', '.join(matched)}.",
                    citation=citation,
                    is_mandatory=is_mandatory
                )
            else:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="FAIL",
                    reason=f"Cultivated crops ({', '.join(user_items)}) do not intersect notified scheme crops.",
                    citation=citation,
                    is_mandatory=is_mandatory
                )

        elif operator == "RANGE":
            num_val = float(val)
            min_v, max_v = float(target_value[0]), float(target_value[1])
            if min_v <= num_val <= max_v:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="PASS",
                    reason=f"Value ({num_val}) is within statutory range [{min_v}, {max_v}].",
                    citation=citation,
                    is_mandatory=is_mandatory
                )
            else:
                return RuleOutcome(
                    rule_code=rule_code,
                    title_en=title_en,
                    title_hi=title_hi,
                    status="FAIL",
                    reason=f"Value ({num_val}) is outside statutory range [{min_v}, {max_v}].",
                    citation=citation,
                    is_mandatory=is_mandatory
                )

        else:
            return RuleOutcome(
                rule_code=rule_code,
                title_en=title_en,
                title_hi=title_hi,
                status="UNKNOWN",
                reason=f"Unsupported rule operator: {operator}",
                citation=citation,
                is_mandatory=is_mandatory
            )

    except (ValueError, TypeError) as err:
        return RuleOutcome(
            rule_code=rule_code,
            title_en=title_en,
            title_hi=title_hi,
            status="UNKNOWN",
            reason=f"Could not parse field value '{val}' ({str(err)}).",
            citation=citation,
            is_mandatory=is_mandatory
        )

def evaluate_scheme(scheme_code: str, profile_data: Dict[str, Any]) -> SchemeEvaluation:
    """
    Evaluates all rules for a scheme and computes overall deterministic status:
    - LIKELY_ELIGIBLE: all mandatory rules are PASS.
    - LIKELY_NOT_ELIGIBLE: any mandatory rule is FAIL.
    - NEEDS_MORE_INFO: at least one mandatory rule is UNKNOWN and none FAIL.
    """
    scheme = SCHEME_CATALOGUE[scheme_code]
    passed_rules: List[RuleOutcome] = []
    failed_rules: List[RuleOutcome] = []
    unknown_rules: List[RuleOutcome] = []

    for rule in scheme.get("rules", []):
        outcome = evaluate_single_rule(rule, profile_data)
        if outcome.status == "PASS":
            passed_rules.append(outcome)
        elif outcome.status == "FAIL":
            failed_rules.append(outcome)
        else:
            unknown_rules.append(outcome)

    # Determine overall status
    has_mandatory_fail = any(r.is_mandatory for r in failed_rules)
    has_mandatory_unknown = any(r.is_mandatory for r in unknown_rules)

    if has_mandatory_fail:
        overall_status = "LIKELY_NOT_ELIGIBLE"
        readiness_state = "NOT_ELIGIBLE"
    elif has_mandatory_unknown:
        overall_status = "NEEDS_MORE_INFO"
        readiness_state = "NEEDS_MORE_INFORMATION"
    else:
        overall_status = "LIKELY_ELIGIBLE"
        readiness_state = "READY_FOR_OFFICIAL_APPLICATION_REVIEW"

    return SchemeEvaluation(
        scheme_code=scheme["scheme_code"],
        official_name_en=scheme["official_name_en"],
        official_name_hi=scheme["official_name_hi"],
        department=scheme["department"],
        level=scheme["level"],
        category=scheme.get("category", "AGRICULTURE_BENEFIT"),
        benefit_type=scheme["benefit_type"],
        benefit_summary_en=scheme["benefit_summary_en"],
        benefit_summary_hi=scheme["benefit_summary_hi"],
        overall_status=overall_status,
        passed_rules=passed_rules,
        failed_rules=failed_rules,
        unknown_rules=unknown_rules,
        official_portal_url=scheme["official_portal_url"],
        verified_at=scheme["verified_at"],
        source_title=scheme["source_title"],
        source_section=scheme["source_section"],
        source_url=scheme["source_url"],
        readiness_state=readiness_state
    )

def evaluate_all_schemes(profile_data: Dict[str, Any], stated_needs: List[str] = None) -> List[SchemeEvaluation]:
    """
    Evaluates all curated schemes for Uttar Pradesh and applies multi-factor transparent ranking:
    Formula: Total = 0.40 * NeedRelevance + 0.35 * EligibilityScore + 0.10 * GeoRelevance + 0.15 * FreshnessScore
    Guarantees that relevance score NEVER overrides a FAIL eligibility result.
    """
    results: List[SchemeEvaluation] = []
    normalized_needs = [str(n).strip().lower() for n in (stated_needs or []) if n]
    
    # Ensure state defaults to Uttar Pradesh if in UP geography
    evaluated_profile = profile_data.copy()
    if "state" not in evaluated_profile:
        evaluated_profile["state"] = "Uttar Pradesh"

    # Evaluate unique schemes (filter out aliases)
    seen_codes = set()
    for scheme_code, scheme_meta in SCHEME_CATALOGUE.items():
        actual_code = scheme_meta.get("scheme_code", scheme_code)
        if actual_code in seen_codes:
            continue
        seen_codes.add(actual_code)

        eval_result = evaluate_scheme(scheme_code, evaluated_profile)
        
        # 1. Need Relevance (0 to 100)
        need_tags = [str(t).lower() for t in scheme_meta.get("need_tags", [])]
        matched_needs = []
        if normalized_needs:
            for need in normalized_needs:
                if any(need in tag or tag in need for tag in need_tags):
                    matched_needs.append(need)
            need_relevance = (len(matched_needs) / max(len(normalized_needs), 1)) * 100.0
            if matched_needs:
                need_relevance = max(need_relevance, 80.0) # Bonus for targeted matches
        else:
            need_relevance = 50.0 # Neutral baseline when no needs specified

        # 2. Eligibility Score (0 to 100)
        if eval_result.overall_status == "LIKELY_ELIGIBLE":
            eligibility_score = 100.0
        elif eval_result.overall_status == "NEEDS_MORE_INFO":
            eligibility_score = 50.0
        else:
            eligibility_score = 0.0

        # 3. Geographic Relevance (0 to 100) & Spatial Applicability
        geo_res = evaluate_geographic_applicability(
            district=evaluated_profile.get("district"),
            state=evaluated_profile.get("state"),
            scheme_code=actual_code,
            primary_crops=evaluated_profile.get("primary_crops")
        )
        geo_relevance = geo_res.geo_score

        # Out-of-State / Geographic Inapplicability Enforcement
        if geo_res.applicability_status == "NOT_APPLICABLE":
            eval_result.overall_status = "LIKELY_NOT_ELIGIBLE"
            eval_result.readiness_state = "NOT_ELIGIBLE"
            eligibility_score = 0.0

        # 4. Evidence Freshness (0 to 100)
        ver_status = scheme_meta.get("verification_status", "VERIFIED")
        if ver_status == "VERIFIED":
            freshness_score = 100.0
        elif ver_status == "REQUIRES_REVIEW":
            freshness_score = 85.0
        elif ver_status == "UNDER_REVIEW":
            freshness_score = 65.0
        elif ver_status in ["OUTDATED", "SUPERSEDED"]:
            freshness_score = 25.0
        else:
            freshness_score = 75.0

        # Composite Multi-Factor Score
        total_score = round(
            (0.40 * need_relevance) +
            (0.35 * eligibility_score) +
            (0.10 * geo_relevance) +
            (0.15 * freshness_score),
            1
        )

        # Formulate human-readable explanation
        if geo_res.applicability_status == "NOT_APPLICABLE":
            reason = f"यह योजना {evaluated_profile.get('state', 'इस क्षेत्र')} में लागू नहीं है (केवल उत्तर प्रदेश राज्य में मान्य)।"
        elif geo_res.is_critical_water_zone and actual_code == "PMKSY_PDMC" and eval_result.overall_status == "LIKELY_ELIGIBLE":
            reason = f"भूजल प्राथमिकता: {geo_res.district} भूजल-संकट ग्रस्त जिला है; ड्रिप/स्प्रिंकलर टोकन प्राथमिकता।"
        elif geo_res.is_aspirational and actual_code == "SMAM_MACHINERY" and eval_result.overall_status == "LIKELY_ELIGIBLE":
            reason = f"आकांक्षी जिला प्राथमिकता: {geo_res.district} में कृषि यंत्र कस्टम हायरिंग सेंटर हेतु विशेष कोटा।"
        elif matched_needs and eval_result.overall_status == "LIKELY_ELIGIBLE":
            reason = f"शीर्ष अनुशंसा: आपकी आवश्यकता '{', '.join(matched_needs)}' से सीधे मेल खाती है और सभी पात्रता शर्तें उत्तीर्ण हैं।"
        elif matched_needs:
            reason = f"आवश्यकता '{', '.join(matched_needs)}' से संबंधित है, परंतु कुछ शर्तों का सत्यापन शेष है।"
        elif eval_result.overall_status == "LIKELY_ELIGIBLE":
            reason = "पात्रता पूर्ण है; सामान्य कृषि संवर्धन योजना।"
        else:
            reason = "नियम अनुसार वर्तमान इनपुट पर अपात्र या जानकारी अपूर्ण।"

        eval_result.ranking_score = total_score
        eval_result.ranking_factors = {
            "need_relevance_pct": round(need_relevance, 1),
            "eligibility_score": eligibility_score,
            "geo_relevance": geo_relevance,
            "evidence_freshness": freshness_score,
            "matched_needs": matched_needs,
            "geo_applicability": geo_res.applicability_status,
            "geo_notes": geo_res.notes,
            "verification_status": ver_status,
            "weights": "40% Needs, 35% Eligibility, 10% Geography, 15% Freshness"
        }
        eval_result.recommendation_reason = reason
        results.append(eval_result)

    # Strict Tiered Ranking:
    # Tier 0: LIKELY_ELIGIBLE (sorted by descending total_score)
    # Tier 1: NEEDS_MORE_INFO (sorted by descending total_score)
    # Tier 2: LIKELY_NOT_ELIGIBLE (sorted by descending total_score)
    tier_order = {"LIKELY_ELIGIBLE": 0, "NEEDS_MORE_INFO": 1, "LIKELY_NOT_ELIGIBLE": 2}
    results.sort(key=lambda x: (tier_order.get(x.overall_status, 3), -(x.ranking_score or 0.0)))

    return results

