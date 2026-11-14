# YojanaSaathi AI — Initial Repository Audit Baseline
**Document Version:** 1.0.0  
**Audit Date:** November 14, 2026  
**Auditor Lead:** Principal Software Architect & QA Lead  
**Scope:** Complete repository inspection (`backend/`, `frontend/`, `data/`, `database`, `deployment`, `documentation`)  
**Product Mission:** Evidence-Grounded Farmer Benefit Intelligence and Multi-Scheme Convergence Platform for Uttar Pradesh (75 Districts)

---

## 1. Executive Summary

An exhaustive, non-destructive audit of the existing **YojanaSaathi AI** codebase was conducted prior to implementing the master transformation. The application already demonstrates a mature architectural foundation:
- A deterministic 3-valued (`PASS`, `FAIL`, `UNKNOWN`) eligibility engine strictly separating policy execution from LLM inference.
- Multi-factor recommendation ranking incorporating need relevance, eligibility thresholds, agro-climatic district zoning, and document freshness.
- Multilingual grounded Q&A with 4 operational modes (Hindi, English, Hinglish, Punjabi).
- A clean, modern Vite React frontend styled with Tailwind CSS, custom field illustrations, and a field-guide aesthetic.
- 41 automated backend tests running cleanly and passing in 6.42 seconds.
- Clean Vite frontend production build compiling in 4.88 seconds.

However, several critical engineering, policy, and workflow gaps require remediation to reach hackathon-winning, production-grade quality (Target: 9.5+/10).

---

## 2. Comprehensive System Architecture Audit (19 Areas)

### 2.1 Frontend Architecture
- **Observed State:** React 19 + TypeScript + Vite + Tailwind CSS. The state management resides primarily in `App.tsx` passing state props down to views (`LandingPage`, `FarmerIntakeWizard`, `RecommendationResultsView`, `ActionPlanView`, `SchemesCatalogueView`, `AdminPortalView`, `GroundedAssistantModal`).
- **Strengths:** Fast compilation, responsive UI, accessible design tokens (`forest-*`, `field-*`, `sand-*`), custom field scene illustration, muted background video.
- **Weaknesses:**
  - Lack of offline caching for generated Action Plans in case of cellular disconnection in rural UP.
  - Natural language intake in `GroundedAssistantModal` currently only answers general scheme Q&A; it does not extract structured farmer parameters or pass them into the eligibility wizard.

### 2.2 Backend Architecture
- **Observed State:** FastAPI application with modular routers (`/api/auth`, `/api/profiles`, `/api/schemes`, `/api/recommendations`, `/api/convergence`, `/api/action-plans`, `/api/assistant`, `/api/admin`).
- **Strengths:** Strict separation between routes, schemas, models, and service engines. Clean dependency injection for database sessions and role authorization.
- **Weaknesses:**
  - Need a dedicated conversational intake service (`/api/assistant/intake`) that extracts structured farmer profiles from conversational Hindi/Hinglish text and flags bigha ambiguity.

### 2.3 Database Models
- **Observed State:** SQLAlchemy ORM models in `backend/app/models/__init__.py`: `User`, `UserRole`, `AuthSession`, `FarmerProfile`, `Consent`, `Scheme`, `SchemeDocumentRequirement`, `SchemeVersion`, `EligibilityRule`, `CompatibilityRule`, `ActionPlan`, `AuditLog`.
- **Strengths:** UUID primary keys, foreign key constraints with explicit `ondelete` actions, indexes on lookup columns, dual-compatibility between SQLite and PostgreSQL.
- **Weaknesses:**
  - Minor schema redundancy where `UP_KISAN_PENSION` was keyed separately from `UP_KRISHAK_DURGHATNA` with duplicate metadata in seeder dictionaries.

### 2.4 Database Migrations
- **Observed State:** Alembic migration version `61caf41f27a3_initial_schema_v3.py` establishes the baseline schema.
- **Strengths:** Clean upgrade path for both SQLite and PostgreSQL.
- **Weaknesses:** Need automated pre-flight checks in deployment scripts to verify migration state before running the API server.

### 2.5 Authentication & Authorization
- **Observed State:** Password hashing with passlib/bcrypt, JWT access tokens with short TTL (60 min), refresh tokens hashed with SHA-256 stored in `auth_sessions` table with family-based rotation and revocation. Role-based access control with `@require_admin` dependency.
- **Strengths:** High security posture, prevents token reuse attacks, supports guest farmer workflows without forcing immediate account creation.
- **Weaknesses:** Rate limiting on auth endpoints should be explicitly enforced in middleware to prevent brute-force attacks.

### 2.6 Eligibility Engine
- **Observed State:** Purely deterministic Python engine in `backend/app/services/eligibility_engine.py`. Evaluates rules using operators `GTE`, `LTE`, `EQUALS`, `IN`, `INTERSECT_ANY`, `RANGE`.
- **Strengths:** Never delegates eligibility to an LLM. Respects 3-valued logic (`PASS`, `FAIL`, `UNKNOWN`). Evaluates land units (converting acres/bigha/hectare).
- **Weaknesses:**
  - The schema returned by `evaluate_scheme` should expose exact prompt-aligned fields (`conditions`, `passed_conditions`, `failed_conditions`, `unknown_conditions`, `missing_information`, `policy_version`, `evidence_references`, `disclaimer`) alongside existing keys to ensure 100% contract compliance.

### 2.7 Recommendation Engine
- **Observed State:** Multi-factor ranking: `0.40 * NeedRelevance + 0.35 * EligibilityScore + 0.10 * GeoRelevance + 0.15 * FreshnessScore`.
- **Strengths:** Strictly guarantees that a high relevance score never elevates a scheme whose mandatory conditions evaluated to `FAIL`.
- **Weaknesses:** Ensure ranking explanations explicitly state the mathematical components for complete judge transparency.

### 2.8 Convergence Engine
- **Observed State:** Pairwise convergence engine in `backend/app/services/convergence_engine.py` evaluating compatibility between scheme pairs.
- **Strengths:** Rejects false transitivity (if A is compatible with B, and B with C, A is not automatically assumed compatible with C). Requires explicit statutory evidence.
- **Weaknesses:** Provide full pairwise evidence matrix covering all 15 possible combinations of the 6 active schemes.

### 2.9 Document Deduplication
- **Observed State:** `readiness_engine.py` groups documents across selected schemes by category (`IDENTITY_PROOF`, `LAND_RECORD`, `BANK_PASSBOOK`, `RESIDENCE_PROOF`, etc.).
- **Strengths:** Farmers prepare Aadhaar or Khatauni once, satisfying multiple simultaneous applications.
- **Weaknesses:** Missing document checklists need clear download/procurement destination guidance (e.g. Tehsil, CSC Center, e-District portal).

### 2.10 Farmer Benefit Action Plan
- **Observed State:** Unique plan identifier generation, selected scheme evaluations, readiness checklists, and official application navigation steps.
- **Strengths:** Clear separation between independent official steps and YojanaSaathi guidance.
- **Weaknesses:** Action plans should be exportable/printable with QR code linking back to the verified digital record.

### 2.11 AI Assistant
- **Observed State:** `backend/app/services/qa_service.py` with multi-language detection (Hindi, English, Hinglish, Punjabi) and grounded answers from official gazette sources.
- **Strengths:** Zero hallucination policy; returns explicit `can_verify: false` when evidence is missing.
- **Weaknesses:** Lacked conversational parameter extraction to allow farmers to state their landholding, crops, and needs in natural voice/text and transition into eligibility checking.

### 2.12 Scheme Catalogue
- **Observed State:** 6 active core schemes:
  1. `PM_KISAN`: Pradhan Mantri Kisan Samman Nidhi
  2. `PMFBY`: Pradhan Mantri Fasal Bima Yojana
  3. `PMKSY_PDMC`: PM Krishi Sinchayee Yojana — Per Drop More Crop
  4. `KCC`: Kisan Credit Card
  5. `UP_KRISHAK_DURGHATNA`: UP Mukhyamantri Krishak Durghatna Kalyan Yojana
  6. `SMAM_MACHINERY`: Sub-Mission on Agricultural Mechanization (Krishi Yantrikikaran)
- **Strengths:** 100% verified live URLs (200 OK), official department citations, and bilingual descriptions.
- **Weaknesses:** `UP_KISAN_PENSION` alias key in `scheme_catalogue.py` caused confusion with Durghatna Kalyan.

### 2.13 Scheme Source Register
- **Observed State:** Gazette citations embedded in scheme metadata.
- **Strengths:** Full references to Ministry of Agriculture, RBI Master Circulars, UP Revenue Department notifications.
- **Weaknesses:** Need standalone tabular register in `docs/policy/POLICY_VERIFICATION_MATRIX.md` and JSON data files in `data/schemes/`.

### 2.14 Admin Verification Workflow
- **Observed State:** Endpoints in `/api/admin` for system overview, audit log inspection, and policy change impact simulation.
- **Strengths:** Tracks affected saved action plans and logs administrative actions.
- **Weaknesses:** UI portal in `AdminPortalView.tsx` needs clear status indicators for policy amendment simulations.

### 2.15 Automated Tests
- **Observed State:** 41 backend tests in `backend/tests/` covering multilingual assistant, auth, convergence, E2E journey, eligibility rules, geographic applicability, and PostgreSQL compatibility.
- **Strengths:** 100% passing rate with fast execution.
- **Weaknesses:** Needs test coverage for conversational natural language intake, bigha unit ambiguity resolution, and Playwright E2E automation.

### 2.16 Docker Configuration
- **Observed State:** Root `docker-compose.yml`, `backend/Dockerfile`, and `frontend/Dockerfile`.
- **Strengths:** Multi-stage builds, non-root user execution, health checks.
- **Weaknesses:** Verify production builds and provide unified one-command startup in `README.md`.

### 2.17 Environment Variables
- **Observed State:** `.env.example` in root with documented variables for `SECRET_KEY`, `DATABASE_URL`, `CORS_ORIGINS`, `ENVIRONMENT`.
- **Strengths:** No committed secrets; sensitive tokens excluded via `.gitignore`.
- **Weaknesses:** Add validation in `core/config.py` for default insecure keys in production mode.

### 2.18 Deployment Configuration
- **Observed State:** Production build verified with Vite and Uvicorn.
- **Strengths:** SQLite default for zero-friction hackathon demos, instant PostgreSQL switch via `DATABASE_URL`.
- **Weaknesses:** Need step-by-step troubleshooting section in `docs/deployment/DEPLOYMENT_GUIDE.md`.

### 2.19 Documentation
- **Observed State:** Existing markdown files scattered across root and `documentation/`.
- **Strengths:** Clear technical descriptions, team attribution (`Team Aalekh`).
- **Weaknesses:** Needs consolidation into the structured `docs/` hierarchy specified in the Master Prompt.

---

## 3. Discovered Weaknesses & Issue Registry

| Issue ID | Severity | Affected Area | Observed Behaviour | Expected Behaviour | Root Cause | Proposed Correction | Verification Test |
|---|---|---|---|---|---|---|---|
| **ISSUE-01** | P1 | AI Assistant / Intake | Natural language conversational input only handled Q&A; could not extract farmer profile attributes for eligibility | Allow farmers to state their situation in Hindi (e.g. 2 bigha wheat farmer needing irrigation), extract profile, ask follow-ups, and run deterministic eligibility | Absence of intake extraction pipeline in `qa_service.py` | Implement `farmer_intake_service.py` with entity extraction & `/api/assistant/intake` endpoint | Unit test with Hindi sentences & verify extracted profile matches criteria |
| **ISSUE-02** | P1 | Unit Ambiguity | "Bigha" conversion previously hardcoded to 0.625 acres (Pucca Bigha) | Must explicitly prompt farmer to confirm whether land is Pucca Bigha (~0.625 acre) or Kachha Bigha (~0.21-0.33 acre) as per UP land revenue customs | Universal bigha assumption in land parser | Add explicit unit ambiguity detection and follow-up prompt in intake service | Test parser with ambiguous bigha inputs |
| **ISSUE-03** | P2 | Scheme Catalogue | `UP_KISAN_PENSION` alias key in catalogue duplicated `UP_KRISHAK_DURGHATNA` | Clean, distinct catalogue entries representing the 6 official schemes | Legacy seeder alias | Standardize on `UP_KRISHAK_DURGHATNA` and clearly document accidental welfare status | Catalogue seeder verification test |
| **ISSUE-04** | P2 | Documentation Hierarchy | Documentation files were in `documentation/` and root instead of `docs/` subdirectories | Standardized `docs/{architecture,product,policy,security,testing,deployment,audit,submission}` layout | Historical incremental development | Reorganize and consolidate documentation suite | Directory structure validation |
| **ISSUE-05** | P2 | Offline Action Plan Access | If rural cellular connection drops, user cannot view previously generated action plan | Cache active plan in browser `localStorage` and provide offline notice | Client-only ephemeral state in React | Implement local storage persistence in `ActionPlanView.tsx` | Disconnect simulation in browser |
| **ISSUE-06** | P2 | Scheme Evaluation Schema | `SchemeEvaluation` schema used `passed_rules` instead of prompt's `passed_conditions` | Support both schema keys seamlessly for backwards compatibility and specification alignment | Schema naming variation | Add prompt-aligned alias fields to `SchemeEvaluation` | Backend test suite execution |

---

## 4. Implementation Priorities & Action Plan

1. **Phase 1 & 2:** Establish `docs/` and `data/` directory hierarchy, generate structured JSON data, and produce cleanup report.
2. **Phase 3:** Create `docs/policy/POLICY_VERIFICATION_MATRIX.md` with complete gazette citations and verification statuses.
3. **Phase 4 & 5:** Harden eligibility engine schema compliance and publish complete pairwise convergence matrix (`docs/policy/CONVERGENCE_EVIDENCE_MATRIX.md`).
4. **Phase 6 & 7:** Implement Hindi Natural Language Farmer Intake (`farmer_intake_service.py`), bigha ambiguity resolution, and connect to frontend modal.
5. **Phase 8, 9, 10:** Document 7-stage farmer benefit journey, document deduplication, and enhance offline resilience and accessibility.
6. **Phase 11 & 12:** Complete security audit, add intake/ambiguity automated tests, and run Playwright E2E test verification.
7. **Phase 13 & 14:** Verify database performance and complete deployment documentation.
8. **Phase 15 & 16:** Finalize documentation consolidation, hackathon demo script, packaging clean submission ZIP, and final engineering score.

---
*End of Baseline Audit Report.*
