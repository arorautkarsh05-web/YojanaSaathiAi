# YojanaSaathi AI — Automated Testing & Quality Assurance Strategy
**Document Version:** 3.0.0  
**Scope:** Backend, Engine Logic, Security Verification, and Playwright E2E Strategy  
**Lead QA Engineer:** QA Automation Engineer & Product Reliability Auditor

---

## 1. Testing Philosophy & Verification Principles

1. **Deterministic Truth:** The core value proposition of YojanaSaathi is absolute correctness. Tests verify that statutory rules never yield probabilistic estimations or hallucinated approvals.
2. **Strict Three-Valued Logic Verification:** Missing information, invalid physical boundaries, or expired policies must evaluate to `UNKNOWN` or `FAIL`. Missing fields are never allowed to evaluate to `PASS`.
3. **No False Transitivity:** Convergence between Scheme $A$ and Scheme $B$, and between $B$ and $C$, is independently tested; no transitive compatibility is permitted without documentary proof.
4. **Honest Reporting:** No synthetic test results are ever reported. Only tests that actually executed are logged.

---

## 2. Test Architecture & Pytest Hierarchy

The automated test suite in `backend/tests/` is organized into distinct domain suites:

```
backend/tests/
├── test_natural_language_intake.py      # Conversational intake, bigha unit ambiguity, missing details
├── test_mandatory_scenarios.py          # 13 core statutory and boundary conditions
├── test_assistant_multilingual.py       # Grounded Q&A across Hindi, English, Hinglish, Punjabi
├── test_eligibility.py                  # 3-valued deterministic rules engine evaluation
├── test_convergence.py                  # Pairwise convergence without transitivity
├── test_geo_and_readiness.py            # 75 UP districts, 6 agro-climatic zones, and document readiness
├── test_auth.py                         # Registration, login, token rotation, and RBAC
├── test_ranking_and_security.py         # Multi-factor ranking and injection defense
├── test_postgresql_compatibility.py     # Dual-engine schema compatibility (SQLite + PostgreSQL)
└── test_e2e_journey.py                  # Full citizen lifecycle from profile to action plan
```

---

## 3. End-to-End Playwright Automation Specification

For cross-browser UI verification, Playwright scenarios test the complete citizen journey:
1. **Scenario 1:** New farmer enters homepage, selects Hindi, opens Grounded Assistant.
2. **Scenario 2:** Farmer submits natural language intake: *"मेरे पास दो बीघा जमीन है और मैं गेहूं की खेती करता हूं। मुझे सिंचाई के लिए सरकारी सहायता चाहिए।"*
3. **Scenario 3:** Assistant extracts parameters, renders the Bigha regional difference notice, prompts for district.
4. **Scenario 4:** Farmer confirms district as Jhansi; system displays one-click evaluation button.
5. **Scenario 5:** Recommendation view displays evaluated schemes (PMKSY-PDMC, PMFBY, KCC, PM-KISAN) with `PASS`, `FAIL`, and `NEEDS_MORE_INFO` statuses.
6. **Scenario 6:** Farmer selects schemes and generates unified Action Plan with 7-stage benefit tracker and deduplicated document checklist.
7. **Scenario 7:** Farmer prints or caches the action plan offline.

