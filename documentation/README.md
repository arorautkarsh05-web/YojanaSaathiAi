# 🌾 YojanaSaathi AI (योजना साथी AI)
> **Evidence-Grounded Farmer Benefit Intelligence & Multi-Scheme Convergence Platform**  
> *Initial Geography: Uttar Pradesh, India (All 75 Districts) | Focus: AgriTech, GovTech, AI for Social Good*

---

## 👥 Team Information (टीम आलेख)

- **Team Name:** Aalekh (टीम आलेख)
- **Team Leader:** Adima Agarwal
- **Team Member:** Utkarsh Arora

---

## 📑 Table of Contents (विषय सूची)
1. [Executive Summary & Core Mission](#1-executive-summary--core-mission)
2. [The Core Problem Solved](#2-the-core-problem-solved)
3. [System Architecture & Technology Stack](#3-system-architecture--technology-stack)
4. [Complete 7-Stage Farmer Benefit Journey](#4-complete-7-stage-farmer-benefit-journey)
5. [Document Verification Center & 1-Click Workflow](#5-document-verification-center--1-click-workflow)
6. [Core Technological Innovations (नवाचार)](#6-core-technological-innovations-नवाचार)
7. [How It Is Different from Other Platforms (पारंपरिक प्रणालियों से भिन्नता)](#7-how-it-is-different-from-other-platforms-पारंपरिक-प्रणालियों-से-भिन्नता)
8. [Multi-Scheme Pairwise Convergence Engine](#8-multi-scheme-pairwise-convergence-engine)
9. [Supported Schemes & Gazette Grounding (6 Statutory Schemes)](#9-supported-schemes--gazette-grounding-6-statutory-schemes)
10. [Data Privacy, Security & DPDP Act 2023 Compliance](#10-data-privacy-security--dpdp-act-2023-compliance)
11. [Offline Resilience & Rural Usability](#11-offline-resilience--rural-usability)
12. [Installation, Setup & Automated Test Suite (105 Tests)](#12-installation-setup--automated-test-suite-105-tests)

---

## 1. Executive Summary & Core Mission

**YojanaSaathi AI (योजना साथी AI)** is a production-grade, evidence-grounded welfare intelligence platform engineered specifically for Indian farmers and rural assistance workers (CSC VLEs, Panchayat Sahayaks, Krishi Mitras).

Unlike generic search portals that display passive lists of government schemes, or generic AI chatbots that hallucinate non-existent subsidies, **YojanaSaathi operates as an intelligent decision-support, document preparation, and multi-scheme convergence engine**.

### 🎯 Core Principles
- **Trustworthiness & Zero Hallucination:** Eligibility evaluation is strictly deterministic via a mathematical 3-valued logic engine (`PASS`, `FAIL`, `UNKNOWN`). The AI never guesses statutory eligibility.
- **Evidence-Backed Convergence:** Discovers synergistic multi-scheme combinations while mathematically preventing double-dipping and circular policy conflicts.
- **Farmer-First Usability:** Designed for multilingual voice/text conversational intake (Hindi, English, Hinglish, Punjabi), automatic colloquial land unit disambiguation (UP Pucca/Kachha Bigha to standard Acres), and complete offline action-plan recovery.
- **Government Boundary Respect:** Explicitly maintains strict statutory separation. YojanaSaathi assists farmers with eligibility understanding, document verification, and official portal directions—it never impersonates a government sanctioning authority.

---

## 2. The Core Problem Solved

Small and marginal farmers in Uttar Pradesh face immense barriers in accessing government agricultural benefits:

1. **Fragmented Portal Ecosystem:** Farmers must independently discover and navigate dozens of disconnected portals (`pmkisan.gov.in`, `pmfby.gov.in`, `edistrict.up.gov.in`, `agridbt.up.gov.in`), each with unique registration requirements.
2. **Exclusion Due to Complex Statutory Criteria:** Farmers miss out on eligible schemes because official guidelines contain complex conditional exclusions (e.g., institutional landholders, income tax payer clauses, constitutional post holders) written in bureaucratic language.
3. **Double-Dipping Fear & Convergence Ignorance:** Farmers avoid applying for multiple benefits out of fear that availing PM-KISAN might disqualify them from PMFBY crop insurance or Kisan Credit Card (KCC) loans, missing out on legal multi-scheme convergence.
4. **Colloquial Land Unit Ambiguities:** In Uttar Pradesh, land area is commonly expressed in **Bigha**, which varies dramatically by region:
   - **Western UP (Pucca Bigha):** $\approx 0.625\text{ acres}$ ($2,529\text{ m}^2$)
   - **Eastern UP & Bundelkhand (Kachha Bigha):** $\approx 0.208 - 0.333\text{ acres}$ ($843 - 1,350\text{ m}^2$)
   A standard 5-Bigha plot could mean either $3.125\text{ acres}$ (ineligible for small-farmer machinery grants) or $1.04\text{ acres}$ (eligible for 55% micro-irrigation subsidy). Existing bots fail to ask for clarification, leading to wrongful disqualification.
5. **Repeated Document Submission:** Farmers submit the same Khatauni land title, Aadhaar, bank passbook, and photos repeatedly across departments without unified deduplication.
6. **Strict Statutory Deadlines:** Critical deadlines (e.g., 72 hours for crop loss intimation under PMFBY, 45 days for accidental claim submission under UP Krishak Durghatna) are frequently missed due to lack of timely, structured guidance.

---

## 3. System Architecture & Technology Stack

YojanaSaathi is built on a modern, decoupled client-server architecture with deterministic engine isolation:

```
┌────────────────────────────────────────────────────────────────────────┐
│                   FARMER & CSC ASSISTANT WORKER UI                     │
│          React 19 • Vite • Tailwind CSS • Lucide Icons • i18n          │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTPS / REST / JSON
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND SERVICE                         │
│       Python 3.13 • Pydantic v2 • SQLAlchemy ORM • Magic Bytes         │
├───────────────────────────────────┬────────────────────────────────────┤
│  • Grounded Conversational Intake │  • Deterministic 3-Valued Rules    │
│  • Bigha Regional Ambiguity Engine│  • Pairwise Convergence Engine     │
│  • Document Verification Center   │  • ReportLab 1-Page PDF Generator  │
│  • Token-Family Replay Revocation │  • DPDP-Compliant Masked Aadhaar   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     DATABASE & STORAGE LAYER                           │
│     SQLite (Zero-Config Dev) / PostgreSQL (Production Compatible)      │
│      Isolated UUID Secure Document Storage Vault (Outside Web Root)    │
└────────────────────────────────────────────────────────────────────────┘
```

### Technology Stack Specifications
- **Frontend:** React 19.0, Vite 6.0, TypeScript 5.8, Tailwind CSS 3.4, `i18next` for Hindi/English localization.
- **Backend:** FastAPI (Python 3.13), Uvicorn ASGI Server, Pydantic v2 data contracts.
- **Database:** SQLAlchemy 2.0 ORM with Alembic schema migrations; dual-dialect support (SQLite + PostgreSQL).
- **Security & Media Validation:** Magic byte binary inspection (`%PDF-`, `\xFF\xD8\xFF`, `\x89PNG`), Argon2 password hashing, JWT bearer tokens with refresh family revocation.
- **Document Generation:** ReportLab 4.4 generating tamper-evident, vector-sharp 1-Page Farmer Benefit Summary PDFs.
- **End-to-End Testing:** Playwright 1.65 Chromium headless browser test suite + Pytest 9.2 (105 tests, 100% pass rate).

---

## 4. Complete 7-Stage Farmer Benefit Journey

YojanaSaathi guides the farmer through an end-to-end, structured 7-stage benefit lifecycle:

```
[1. Profile Intake] ➔ [2. Eligibility Check] ➔ [3. Gap Resolution] ➔ [4. Document Verification]
                                                                               │
[7. Government Sanction] 🠤 [6. Farmer Progress] 🠤 [5. Official Next Steps] 🠤───┘
         │
         ▼
[1-Page Printable Farmer Benefit Summary PDF]
```

1. **Stage 1 — Profile Intake:** Farmer specifies district (all 75 UP districts supported), landholding, crops, irrigation status, and social category via interactive form or natural language conversational intake.
2. **Stage 2 — Deterministic Eligibility Assessment:** 3-valued logic engine evaluates statutory rules across all 6 gazetted schemes, returning `ELIGIBLE`, `INELIGIBLE`, or `NEEDS_MORE_INFO`.
3. **Stage 3 — Missing Information Resolution:** Identifies exact missing attributes (e.g., institutional landownership, Aadhaar seeding status, bank link) and prompts the farmer to resolve ambiguities.
4. **Stage 4 — Document Verification Center:** Consolidated checklist with 1-click tick-box verification for general documents and secure magic-byte auto-verified upload for Aadhaar and Photograph.
5. **Stage 5 — Official Next Steps:** Interactive step-by-step roadmap with official portal deep-links (`pmkisan.gov.in`, `upagripardarshi.gov.in`), CSC physical touchpoints, and application tracking numbers.
6. **Stage 6 — Farmer-Reported Progress Tracker:** 1-click tick-box allowing farmers to confirm application submission on the respective government portal (`APPLICATION_SUBMITTED`).
7. **Stage 7 — Government Verification & Sanction:** 1-click departmental sanction verification tracker reflecting official DBT approval status (`GOVERNMENT_VERIFIED`).
8. **Final Confirmation & Summary:** Unlocks upon completion of all 7 stages to generate the tamper-evident, official **1-Page Farmer Benefit Summary PDF**.

---

## 5. Document Verification Center & 1-Click Workflow

Stage 4 provides an intuitive, high-speed document verification center designed specifically for low-literacy rural usability:

### A. 1-Click Verification for Standard Documents
For standard supporting documents (such as Khatauni land records, Bank Passbook, Income Certificate, Caste Certificate, Soil Health Card):
- The interface displays an interactive **Tick-Box (Checkbox)**.
- With a single click (`1-Click`), the farmer confirms availability.
- The document is instantly marked **`VERIFIED` (सत्यापित)** and persisted in the database as ready for physical CSC presentation.

### B. Auto-Verified Secure Upload for Photo & Aadhaar
- File upload is strictly reserved for **Photograph (`doc_photo`)** and **Aadhaar Card (`doc_aadhaar`)**.
- **Instant Auto-Verification:** When the farmer uploads the file, the backend performs magic-byte validation and instantly flags the document as **`VERIFIED` (`AUTO_VERIFIED_AI`)**.
- **No Manual Reviewer Bottleneck:** Farmers do not have to wait for manual reviewer simulation; the upload immediately advances the workflow.

### C. Cross-Scheme Document Deduplication
If Aadhaar or Khatauni is required by 3 different recommended schemes (e.g., PM-KISAN, PMKSY, KCC), the document appears **only once** in the consolidated checklist, tagged with all shared schemes.

---

## 6. Core Technological Innovations (नवाचार)

YojanaSaathi introduces six foundational technological innovations:

### 1. Deterministic Three-Valued Logic Engine (`PASS`, `FAIL`, `UNKNOWN`)
- **The Problem in Conventional AI:** Standard LLMs hallucinate eligibility. They frequently tell non-farmers or institutional landholders they qualify for PM-KISAN, or invent fictitious grant percentages.
- **The YojanaSaathi Innovation:** All eligibility rules are decoupled from the LLM and evaluated via deterministic mathematical logic over Kleene 3-valued algebra:
  - $\text{TRUE} \land \text{UNKNOWN} = \text{UNKNOWN}$
  - $\text{FALSE} \land \text{UNKNOWN} = \text{FALSE}$
- If any statutory criterion is missing (e.g., land title status or PM-KISAN eKYC), the engine returns `UNKNOWN` with an explicit list of missing parameters, preventing both false rejections and false entitlements.

### 2. Multi-Scheme Pairwise Convergence Engine ($\binom{6}{2}=15$ Combinations)
- **The Problem:** Farmers do not know which schemes can be legally combined. Schemes are designed by different ministries (Ministry of Agriculture, Ministry of Jal Shakti, UP State Revenue Department) with conflicting convergence rules.
- **The YojanaSaathi Innovation:** Computes exact pairwise compatibility across all 15 scheme combinations:
  - **Bundelkhand Special Convergence Incentive:** Bundelkhand farmers automatically receive a +10% higher grant tier under PMKSY (PDMC) drip irrigation.
  - **Anti-Transitivity & Circularity Prevention:** Just because Scheme A is compatible with Scheme B, and Scheme B is compatible with Scheme C, Scheme A is **NOT** blindly assumed compatible with Scheme C. Every pair has an independent statutory gazette evidence citation.

### 3. Regional Colloquial Unit Disambiguation (UP Bigha Resolution)
- **The Problem:** A farmer from Jhansi says *"मेरे पास 3 बीघा जमीन है"* while a farmer from Meerut says *"मेरे पास 3 बीघा जमीन है"*. In Western UP, 3 Bigha is $1.875\text{ acres}$; in Eastern UP, 3 Bigha is $0.75\text{ acres}$. Conventional portals fail to handle this distinction.
- **The YojanaSaathi Innovation:** The natural language intake engine maps the farmer's selected district to its Agro-Climatic Zone (e.g., Western Plain Zone vs. Bundelkhand / Eastern Plain Zone) and prompts with localized conversion options, preventing fatal statutory landholding errors.

### 4. PWA Dual-State Offline Resilience
- **The Problem:** Rural field workers and farmers often lose internet connectivity in interior village fields.
- **The YojanaSaathi Innovation:** Complete action plans, eligibility verdicts, and verified document checklists are mirrored in device `localStorage`. The system survives browser process termination and re-renders full action plans and official portal instructions without an internet connection.

### 5. Magic-Byte Binary Inspection & DPDP Act 2023 Masking
- **The Problem:** Malicious file uploads (renaming `.exe` to `.pdf`) and Aadhaar data leaks.
- **The YojanaSaathi Innovation:** File validation inspects initial file byte signatures (`%PDF-`, `\xFF\xD8\xFF`, `\x89PNG\r\n\x1a\n`) rather than trusting user-supplied MIME extensions. Aadhaar numbers are never stored in plain text; all representations are masked to the last 4 digits (`******3210`) in full compliance with the Digital Personal Data Protection Act 2023.

### 6. Official 1-Page Farmer Benefit Summary (PDF)
- Generates a high-density, vector-rendered 1-page PDF using ReportLab with a unique reference number (`FBS-UP-20261114-XXXXXX`), verified document checklist, convergence roadmap, and a prominent statutory notice: *"NOT A GOVERNMENT CERTIFICATE — INDEPENDENT PREPARATION ROADMAP"*.

---

## 7. How It Is Different from Other Platforms (पारंपरिक प्रणालियों से भिन्नता)

| Feature / Dimension | Traditional Portals (e.g., myScheme, State Portals) | Generic AI Chatbots (e.g., ChatGPT, WhatsApp Bots) | YojanaSaathi AI (योजना साथी AI) |
|---|---|---|---|
| **Eligibility Assessment** | Static keyword search; manual PDF reading required. | Probabilistic / Hallucinatory; invents criteria and subsidies. | **Deterministic 3-Valued Logic Engine (`PASS`, `FAIL`, `UNKNOWN`). Zero hallucination.** |
| **Multi-Scheme Convergence** | ❌ None. Treats each scheme as an isolated silo. | ⚠️ Unreliable. Guesswork without legal gazette citations. | **✅ All 15 pairwise relationships verified with gazette citations & anti-transitivity guarantees.** |
| **Regional Land Units (Bigha)** | ❌ Only accepts standard Acres/Hectares; farmers get confused. | ❌ Uses single nationwide multiplier, causing disqualification. | **✅ 75-District Agro-Climatic Unit Disambiguation (Pucca vs. Kachha Bigha).** |
| **Document Management** | ❌ Repeat uploads across 5 different portals. | ❌ Cannot verify or manage documents. | **✅ 1-Click Verification + Cross-Scheme Deduplication + Magic-Byte Auto-Verify.** |
| **Actionable Roadmap** | ❌ Static text list of requirements. | ❌ High-level generic bullet points. | **✅ 7-Stage Interactive Journey with portal links, progress tracking & sanction confirmation.** |
| **Deliverable Output** | ❌ Web page bookmarks. | ❌ Chat text transcript. | **✅ Official 1-Page Printable Farmer Benefit Summary PDF for CSC submission.** |
| **Offline Usability** | ❌ Fails completely without internet. | ❌ Fails completely without internet. | **✅ Full PWA Offline Recovery (Cached Action Plan & Verified Checklist).** |
| **Statutory Safeguards** | ⚠️ Complex disclaimer buried in footer. | ❌ Frequently claims "You are approved for ₹50,000". | **✅ Clear "NOT A GOVT CERTIFICATE" legal distinction at every workflow stage.** |

---

## 8. Multi-Scheme Pairwise Convergence Engine

Across our 6 statutory schemes, there are exactly $\binom{6}{2} = 15$ unique pairwise combinations. Every pair is independently audited and backed by statutory orders:

1. **PM-KISAN + KCC:** Fully Compatible. PM-KISAN beneficiaries are fast-tracked for simplified KCC issuance under Joint MoA Guidelines.
2. **PM-KISAN + PMFBY:** Fully Compatible. Direct income support complements statutory crop insurance against natural calamities.
3. **PM-KISAN + PMKSY (PDMC):** Fully Compatible. PM-KISAN funds can be utilized for the farmer's 45% margin share in drip irrigation.
4. **PM-KISAN + UP Krishak Durghatna:** Fully Compatible. Income support coexists with state accidental disability/death coverage.
5. **PM-KISAN + SMAM (Mechanization):** Fully Compatible. Tractor and implement subsidies operate on separate capital assistance tracks.
6. **PMFBY + KCC:** Fully Compatible. KCC loan accounts for notified crops are integrated with PMFBY premium debits.
7. **PMFBY + PMKSY (PDMC):** Fully Compatible. Insured crops benefit from micro-irrigation yield stability.
8. **PMFBY + UP Krishak Durghatna:** Fully Compatible. Crop loss indemnification is completely distinct from personal accident insurance.
9. **PMFBY + SMAM:** Requires Verification. Operational guidelines require verifying that customized farm machinery is maintained in insurable conditions.
10. **PMKSY + KCC:** Fully Compatible. Subsidized KCC credit can finance the micro-irrigation farmer contribution.
11. **PMKSY + SMAM:** Fully Compatible. Drip systems and agricultural machinery provide comprehensive farm modernization.
12. **PMKSY + UP Krishak Durghatna:** Fully Compatible. Asset creation coexists with personal insurance.
13. **KCC + SMAM:** Fully Compatible. KCC investment credit limits can be drawn for subsidized farm machinery purchases.
14. **KCC + UP Krishak Durghatna:** Fully Compatible. Credit access coexists with state welfare safety net.
15. **UP Krishak Durghatna + SMAM:** Fully Compatible. Farmer welfare coverage is unaffected by machinery acquisition.

---

## 9. Supported Schemes & Gazette Grounding (6 Statutory Schemes)

| Code | Official Name | Department / Level | Primary Benefit | Gazette Reference |
|---|---|---|---|---|
| `PM_KISAN` | Pradhan Mantri Kisan Samman Nidhi | MoA&FW, Central | ₹6,000/year DBT (3 installments of ₹2,000) | Operational Guidelines 2019 (Rev. 2023) |
| `PMFBY` | Pradhan Mantri Fasal Bima Yojana | MoA&FW, Central | Comprehensive crop insurance (1.5%-2% premium) | Revised Operational Guidelines 2020 |
| `PMKSY_PDMC` | PM Krishi Sinchayee Yojana (PDMC) | MoA&FW / UP Agri, Central+State | 45%-55% subsidy on Drip/Sprinkler (+10% Bundelkhand) | UP Agriculture DBT Guidelines 2023 |
| `KCC` | Kisan Credit Card Scheme | RBI / NABARD, Central | Subsidized crop loan up to ₹3 Lakh at 4% effective interest | RBI Master Circular FIDD.CO.FSD.BC.No.6 |
| `UP_KRISHAK_DURGHATNA` | UP Mukhyamantri Krishak Durghatna Kalyan | UP Revenue Dept, State | Up to ₹5 Lakh compensation for accidental death/disability | UP Shasanadesh No. 12/2020/124 |
| `SMAM_MACHINERY` | Sub-Mission on Agricultural Mechanization | MoA&FW / UP Agri, Central+State | 40%-50% subsidy on farm machinery & Custom Hiring Centers | SMAM Operational Guidelines 2021 |

---

## 10. Data Privacy, Security & DPDP Act 2023 Compliance

1. **Zero-Aadhaar Persistence:** Full 12-digit Aadhaar numbers are strictly barred from database tables. All Aadhaar inputs are truncated and masked to the last 4 digits (`******1234`).
2. **Binary Magic-Byte Inspection:** All uploaded files are inspected at the binary byte level to reject disguised executable files and MIME-type spoofing.
3. **Session Replay Protection:** JWT refresh tokens employ session family rotation. If a stolen refresh token is used, the entire token family is revoked immediately.
4. **Isolated Document Vault:** Documents are saved using random UUID filenames in a protected folder located completely outside the web root.
5. **Auditable Verification Trail:** Every document review, stage toggle, and final confirmation logs an immutable audit event (`AuditLog`).

---

## 11. Offline Resilience & Rural Usability

- **Low-Bandwidth Optimization:** Frontend production bundle is optimized to ~132 KB (gzip) with zero bulky UI component libraries.
- **Offline Action Plan Cache:** When an action plan is generated, it is automatically written to the browser's persistent `localStorage`.
- **Field Tested via Playwright:** Automated end-to-end testing verifies that even when the browser is completely closed and reopened in an offline state (simulating no connectivity in a village field), the farmer's action plan and verified checklist load instantly.

---

## 12. Installation, Setup & Automated Test Suite (105 Tests)

### Prerequisites
- Python 3.11+ (Python 3.13 recommended)
- Node.js 18+ & npm
- Chrome browser (for Playwright E2E testing)

### Backend Setup
```bash
# Clone the repository
git clone https://github.com/arorautkarsh05-web/YojanaSaathi-AI.git
cd YojanaSaathi

# Create and activate Python virtual environment
python -m venv venv
venv\Scripts\activate       # Windows PowerShell
# source venv/bin/activate  # Linux / macOS

# Install backend dependencies
pip install -r backend/requirements.txt

# Start backend server (runs on http://127.0.0.1:8000)
uvicorn app.main:app --app-dir backend --reload --port 8000
```

### Frontend Setup
```bash
# In a new terminal:
cd frontend
npm install
npm run dev                 # Starts Vite dev server on http://localhost:5173
```

### Running the Test Suite (105 Tests, 100% Pass Rate)
```bash
# Run all Pytest backend tests
pytest backend/tests/ -v

# Run Playwright End-to-End Automated Browser Suite
python scripts/run_playwright_e2e.py
```

---

### 🏛️ Statutory Disclaimer
*YojanaSaathi AI is an independent, evidence-grounded welfare intelligence platform developed by Team Aalekh. It is NOT an official government application or certificate. All scheme recommendations and preparation plans are derived strictly from published gazette rules, and official benefit sanction remains the sole discretion of the respective government authority.*
