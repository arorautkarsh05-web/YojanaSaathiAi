"""
Multi-Scheme Convergence Engine.
Evaluates pairwise scheme compatibility based strictly on approved authoritative source evidence.
Never guesses or generalizes compatibility across pairs. Unverified combinations return UNKNOWN_REQUIRES_VERIFICATION.
"""

from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.services.scheme_catalogue import CONVERGENCE_REGISTER
from app.schemas import PairwiseConvergence
from app.models import CompatibilityRule

def find_pairwise_evidence(code_a: str, code_b: str, db: Optional[Session] = None) -> PairwiseConvergence:
    """
    Looks up pairwise evidence in either direction (A, B) or (B, A).
    Queries database table 'compatibility_rules' as primary source of truth,
    falling back to CONVERGENCE_REGISTER.
    Returns UNKNOWN_REQUIRES_VERIFICATION if no human-reviewed authoritative evidence exists.
    """
    if db is not None:
        try:
            rule = db.query(CompatibilityRule).filter(
                ((CompatibilityRule.scheme_code_a == code_a) & (CompatibilityRule.scheme_code_b == code_b)) |
                ((CompatibilityRule.scheme_code_a == code_b) & (CompatibilityRule.scheme_code_b == code_a))
            ).first()
            if rule:
                v_at = rule.verified_at.isoformat() if hasattr(rule.verified_at, "isoformat") else str(rule.verified_at)
                return PairwiseConvergence(
                    scheme_code_a=code_a,
                    scheme_code_b=code_b,
                    status=rule.status,
                    evidence_text=rule.evidence_text,
                    authoritative_source=rule.authoritative_source,
                    source_section=rule.source_section,
                    verified_by=rule.verified_by,
                    verified_at=v_at
                )
        except Exception:
            # Fall back to in-memory register if DB query fails during initialization
            pass

    for entry in CONVERGENCE_REGISTER:
        a = entry["scheme_code_a"]
        b = entry["scheme_code_b"]
        if (a == code_a and b == code_b) or (a == code_b and b == code_a):
            return PairwiseConvergence(
                scheme_code_a=code_a,
                scheme_code_b=code_b,
                status=entry["status"],
                evidence_text=entry["evidence_text"],
                authoritative_source=entry["authoritative_source"],
                source_section=entry["source_section"],
                verified_by=entry["verified_by"],
                verified_at=entry["verified_at"]
            )

    # Trust rule: Missing or unverified evidence returns UNKNOWN_REQUIRES_VERIFICATION
    return PairwiseConvergence(
        scheme_code_a=code_a,
        scheme_code_b=code_b,
        status="UNKNOWN_REQUIRES_VERIFICATION",
        evidence_text="No approved statutory gazette or inter-departmental convergence resolution on file for this combination. Consult your local District Agriculture Officer or Tehsil counter before simultaneous application.",
        authoritative_source="Pending Inter-Departmental Review",
        source_section="General Public Administration Principle",
        verified_by="YojanaSaathi Policy Audit Desk",
        verified_at="2026-01-20T00:00:00Z"
    )

def check_multi_scheme_convergence(scheme_codes: List[str], db: Optional[Session] = None) -> List[PairwiseConvergence]:
    """
    Generates all distinct pairwise combinations for the selected schemes.
    Does NOT generalize one pair's status to the entire group.
    """
    pairs: List[PairwiseConvergence] = []
    unique_codes = list(dict.fromkeys(scheme_codes)) # preserve order while removing duplicates
    
    for i in range(len(unique_codes)):
        for j in range(i + 1, len(unique_codes)):
            pair_result = find_pairwise_evidence(unique_codes[i], unique_codes[j], db=db)
            pairs.append(pair_result)

    return pairs

def get_convergence_graph(scheme_codes: List[str] = None, db: Optional[Session] = None):
    """
    Constructs a topological convergence graph for the specified schemes (or all active schemes).
    Nodes represent statutory schemes; edges represent evidence-backed compatibility relationships.
    """
    from app.services.scheme_catalogue import SCHEME_CATALOGUE
    from app.schemas import GraphNode, GraphEdge, ConvergenceGraphResponse

    target_codes = scheme_codes if scheme_codes else [
        "PM_KISAN", "PMFBY", "PMKSY_PDMC", "KCC", "UP_KRISHAK_DURGHATNA", "SMAM_MACHINERY"
    ]
    unique_codes = list(dict.fromkeys(target_codes))

    nodes: List[GraphNode] = []
    for code in unique_codes:
        meta = SCHEME_CATALOGUE.get(code)
        if meta:
            nodes.append(GraphNode(
                id=meta.get("scheme_code", code),
                label_en=meta.get("official_name_en", code),
                label_hi=meta.get("official_name_hi", code),
                category=meta.get("category", "AGRICULTURE_BENEFIT"),
                department=meta.get("department", "Government of Uttar Pradesh"),
                overall_status="UNKNOWN"
            ))

    edges: List[GraphEdge] = []
    for i in range(len(unique_codes)):
        for j in range(i + 1, len(unique_codes)):
            pair = find_pairwise_evidence(unique_codes[i], unique_codes[j], db=db)
            edges.append(GraphEdge(
                source=pair.scheme_code_a,
                target=pair.scheme_code_b,
                status=pair.status,
                evidence_text=pair.evidence_text,
                authoritative_source=pair.authoritative_source,
                source_section=pair.source_section,
                verified_by=pair.verified_by
            ))

    return ConvergenceGraphResponse(nodes=nodes, edges=edges)

