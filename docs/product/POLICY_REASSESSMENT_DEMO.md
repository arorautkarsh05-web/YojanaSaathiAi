# Statutory Policy Amendment & Citizen Reassessment Architecture
## YojanaSaathi AI — Dynamic Gazette Change Adaptation Engine

**Date**: November 2026  
**Audience**: Hackathon Evaluation Jury, State IT/Agriculture Departments  
**Executable Script**: [`scripts/demo_policy_reassessment.py`](file:///d:/YojanaSaathi/scripts/demo_policy_reassessment.py)  
**Jurisdiction**: Uttar Pradesh, India (All 75 Districts)

---

## 1. The Real-World Government Problem

In agricultural governance, government schemes are **never static**:
1. Eligibility thresholds change when states issue budget-session Government Orders (e.g., relaxing land limits in drought-hit districts like Bundelkhand).
2. Subsidy rates are revised based on fiscal allocations (e.g., from 55% to 80% for marginal farmers).
3. Cutoff dates, crop cluster notifications, and exclusion clauses evolve seasonally.

### The Failure of Traditional Solutions
- **Static Portal Guides & Pamphlets**: Become obsolete within months, causing farmers to submit rejected applications.
- **Generic LLM Chatbots**: Hallucinate outdated rules or mix up notifications from different years, providing incorrect advice with unwarranted confidence.
- **Siloed Department Portals**: Do not notify citizens when a previously ineligible scheme becomes accessible.

---

## 2. YojanaSaathi AI's Innovation: Active Downstream Policy Intelligence

YojanaSaathi AI solves this through a 5-stage automated policy governance pipeline:

```
[ Government Gazette / G.O. Issued ]
                 │
                 ▼
[ 1. Admin Version Ingestion (REST API: /api/v1/admin/policy-impact) ]
                 │
                 ▼
[ 2. Downstream Impact Detection across Saved Citizen Plans ]
                 │
                 ▼
[ 3. Deterministic Three-Valued Reassessment (PASS / FAIL / UNKNOWN) ]
                 │
                 ▼
[ 4. Automated Plan Delta & Convergence Unlocking ]
                 │
                 ▼
[ 5. Immutable Administrative Audit Trail (audit_logs table) ]
```

---

## 3. Step-by-Step Demonstration Walkthrough

You can execute the live demonstration script at any time:
```powershell
.\venv\Scripts\python.exe scripts/demo_policy_reassessment.py
```

### Scenario: Marginal Farmer in Bundelkhand (Jhansi)
A marginal farmer in Jhansi district holds **0.15 acres** of cultivable land with an assured borewell water source and cultivates wheat and gram.

#### Step 1: Baseline Evaluation (v3.0 Rules)
- **PM-KISAN**: Minimum threshold is 0.01 acres $\rightarrow$ **LIKELY_ELIGIBLE** (`PASS`).
- **PMKSY-PDMC (Micro-Irrigation)**: Baseline statutory rule (`RULE_PMKSY_LAND`) requires **$\ge$ 0.20 acres** $\rightarrow$ **LIKELY_NOT_ELIGIBLE** (`FAIL`).
- **Initial Action Plan**: Generated only for PM-KISAN (#YS-UP-20261114-XXXXXX).

#### Step 2: State Cabinet Notification
The Uttar Pradesh Department of Horticulture issues **G.O. Hort/2026/04**:
> *"In view of recurrent water stress in the Bundelkhand region, the minimum cultivable landholding requirement for micro-irrigation installation under PMKSY-PDMC is relaxed from 0.20 acres to 0.10 acres for the 7 Bundelkhand districts (Jhansi, Banda, Chitrakoot, Hamirpur, Jalaun, Lalitpur, Mahoba)."*

#### Step 3: Administrative Impact Assessment
The authorized review desk calls the admin impact endpoint:
```http
POST /api/v1/admin/policy-impact
Content-Type: application/json

{
  "scheme_code": "PMKSY_PDMC",
  "new_version_tag": "v3.1-Bundelkhand-Relaxation",
  "amendment_summary": "UP Govt Order Hort/2026/04: Minimum landholding requirement for micro-irrigation in Bundelkhand relaxed to 0.10 acres."
}
```

**System Response**:
```json
{
  "scheme_code": "PMKSY_PDMC",
  "new_version_tag": "v3.1-Bundelkhand-Relaxation",
  "assessed_at": "2026-11-14T08:43:46.596074Z",
  "affected_plans_count": 2,
  "affected_users_count": 1,
  "status": "IMPACT_EVALUATED",
  "recommended_action": "Mark affected plans with 'NEEDS_REASSESSMENT' status badge."
}
```

#### Step 4: Automated Reassessment Results
The deterministic rules engine re-evaluates the citizen's confirmed physical profile against the amended threshold:
- **PMKSY-PDMC**: 0.15 acres $\ge$ 0.10 acres target $\rightarrow$ **Status transforms from `LIKELY_NOT_ELIGIBLE` to `LIKELY_ELIGIBLE`!**
- **Convergence Unlocked**: The system automatically identifies that PM-KISAN cash flows can now co-finance the beneficiary share of the PMKSY drip irrigation subsidy.

#### Step 5: Updated Action Plan Issued
The citizen receives an updated action plan containing:
1. Both PM-KISAN and PMKSY-PDMC application milestones.
2. Synchronized document checklist expanding from 3 to 5 verified items (including UP Horticulture DBT token receipt).
3. Preserved plan history ensuring no administrative disconnect.

#### Step 6: Immutable Audit Trail
The administrative event is permanently recorded in the database `audit_logs` table:
```json
{
  "action": "POLICY_AMENDMENT_IMPACT_ASSESSED",
  "resource_type": "SCHEME",
  "resource_id": "PMKSY_PDMC",
  "metadata": {
    "scheme_code": "PMKSY_PDMC",
    "new_version": "v3.1-Bundelkhand-Relaxation",
    "amendment_summary": "UP Govt Order Hort/2026/04: Minimum landholding requirement for micro-irrigation in Bundelkhand relaxed to 0.10 acres.",
    "affected_plans_count": 2,
    "affected_users_count": 1
  }
}
```

---

## 4. Key Differentiators for Hackathon Judges

| Capability | Generic Chatbots / Static Portals | YojanaSaathi AI |
|---|---|---|
| **Response to Policy Changes** | Delivers stale or contradictory advice | Automated impact detection across all active citizen plans |
| **Eligibility Re-evaluation** | Farmer must know a rule changed and ask again | Deterministic re-evaluation triggered by version amendment |
| **Audit Compliance** | Zero administrative visibility | Immutable audit logs with affected counts and admin IDs |
| **Convergence Impact** | Unaware of inter-scheme relationships | Automatically unlocks paired convergence opportunities |
| **Grounding Guarantee** | May invent non-existent government amendments | Requires gazette reference, section citation, and verified desk identity |
