# YojanaSaathi AI — Automated Test Execution & Verification Results
**Execution Timestamp:** November 14, 2026, 13:44:00 UTC+05:30  
**Test Framework:** Pytest 9.2.0 | Python 3.13.7 | AnyIO 4.16.0 | Windows 11  
**Build Status:** **57 PASSED | 0 FAILED | 0 SKIPPED (100% Pass Rate)**  
**Execution Duration:** 14.89 seconds

---

## 1. Test Suite Summary Table

| Test Module | Discovered Tests | Passed | Failed | Skipped | Execution Time |
|---|---|---|---|---|---|
| `test_natural_language_intake.py` | 4 | 4 | 0 | 0 | 0.42s |
| `test_mandatory_scenarios.py` | 13 | 13 | 0 | 0 | 1.15s |
| `test_assistant_multilingual.py` | 8 | 8 | 0 | 0 | 0.85s |
| `test_auth.py` | 5 | 5 | 0 | 0 | 1.82s |
| `test_convergence.py` | 4 | 4 | 0 | 0 | 0.38s |
| `test_e2e_journey.py` | 2 | 2 | 0 | 0 | 2.10s |
| `test_eligibility.py` | 8 | 8 | 0 | 0 | 0.65s |
| `test_geo_and_readiness.py` | 8 | 8 | 0 | 0 | 0.72s |
| `test_postgresql_compatibility.py` | 2 | 2 | 0 | 0 | 4.90s |
| `test_ranking_and_security.py` | 4 | 4 | 0 | 0 | 1.80s |
| **TOTAL** | **57** | **57** | **0** | **0** | **14.89s** |

---

## 2. Key Scenario Verification Highlights

1. **Phase 7 Hindi Conversational Intake:**
   - Input: *"मेरे पास दो बीघा जमीन है और मैं गेहूं की खेती करता हूं। मुझे सिंचाई के लिए सरकारी सहायता चाहिए।"*
   - Verified: Correctly parsed intent (`irrigation_subsidy`), crops (`wheat`), landholding unit (`bigha`), and raw text (`2.0 बीघा`).
   - Verified: Triggered `LOCAL_UNIT_VARIATION` ambiguity notice prompting farmer to confirm Pucca vs. Kachha Bigha.
   - Verified: Identified missing `district` and returned targeted follow-up question.

2. **Phase 4 & 5 Deterministic Logic & Anti-Transitivity:**
   - Evaluated 6 schemes across 75 districts.
   - Mandatory rules verified: zero false `PASS` results when attributes are omitted or blank.
   - Pairwise convergence verified: `PMFBY` and `SMAM_MACHINERY` correctly returns `UNKNOWN_REQUIRES_VERIFICATION` due to lack of approved inter-departmental circular.

3. **Phase 11 Security & Auth:**
   - Registration, JWT generation, password verification, and token rotation verified.
   - Horizontal and vertical privilege checks verified.

4. **Phase 13 Database Dual-Compatibility:**
   - Schema successfully created and verified against both SQLite and PostgreSQL dialects with clean transaction rollback.

---

## 3. Frontend Production Build Verification
- Bundler: Vite 8.3.8 + TypeScript 5.8
- Result: 2,126 modules transformed cleanly in 1.51 seconds.
- Output: `dist/index.html` (0.99 kB), `dist/assets/index.js` (419 kB / 122 kB gzip), `dist/assets/index.css` (53.5 kB / 9.0 kB gzip). Zero TypeScript compilation warnings.
