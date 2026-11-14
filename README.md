# 🌾 YojanaSaathi AI (योजना साथी AI)

### Evidence-Grounded Farmer Benefit Intelligence & Multi-Scheme Convergence Platform

**Bridging the gap between farmers and government welfare through transparent, explainable and evidence-driven technology.**

YojanaSaathi AI is a farmer-centric welfare intelligence platform designed to help farmers discover relevant government schemes, understand their eligibility, identify missing requirements and navigate multiple benefits through a unified action plan.

Unlike conventional scheme discovery platforms, YojanaSaathi focuses on **deterministic eligibility evaluation, evidence-backed recommendations and multi-scheme convergence rather than generic AI-generated answers.**

📍 **Initial Geography:** Uttar Pradesh, India (All 75 Districts)  
🌐 **Languages:** हिन्दी | English | Hinglish | ਪੰਜਾਬੀ  
🎯 **Domain:** AgriTech | GovTech | AI for Social Impact

---

## 👥 Team Aalekh

| Team Member | Role |
|---|---|
| **Adima Agarwal** | Team Leader |
| **Utkarsh Arora** | Team Member |

[![Tests](https://img.shields.io/badge/Pytest-57%20Passed%20(100%25)-brightgreen.svg)](docs/testing/TEST_RESULTS.md)
[![Frontend](https://img.shields.io/badge/Vite%20React%2019-Production%20Build%20Clean-blue.svg)](frontend/)
[![Architecture](https://img.shields.io/badge/Deterministic%20Core-3--Valued%20Logic-forest.svg)](docs/architecture/SYSTEM_ARCHITECTURE.md)
[![Coverage](https://img.shields.io/badge/UP%20Geography-All%2075%20Districts-success.svg)](data/district_metadata/up_districts.json)
[![Statutory Links](https://img.shields.io/badge/Government%20Links-100%25%20Live%20(200%20OK)-emerald.svg)](docs/policy/POLICY_VERIFICATION_MATRIX.md)

---

## 🚨 1. The Problem We Are Solving

India has numerous central and state government welfare schemes designed to support farmers. However, discovering and accessing these benefits remains challenging:

- **Fragmented information** across dozens of disconnected departmental portals.
- **Difficulty understanding complicated eligibility conditions** and threshold rules.
- **Uncertainty about which schemes match agricultural needs** across different seasons.
- **Repeated document submission requirements** with no cross-scheme deduplication.
- **Limited awareness of scheme convergence possibilities** and fear of double-dipping.
- **Colloquial Unit Ambiguities:** In UP, land is often stated in "Bigha", which varies between Western UP (Pucca Bigha ~0.625 acres) and Eastern UP (Kachha Bigha ~0.21-0.33 acres). A single conversion multiplier causes statutory disqualification.
- **Language and digital accessibility barriers** on low-bandwidth rural networks.

---

## 💡 2. Our Solution

YojanaSaathi AI transforms fragmented government welfare information into an understandable, evidence-grounded farmer benefit intelligence system.

Instead of asking farmers to search through dozens of schemes individually, the platform follows their actual agricultural needs:

1. **Which government schemes are relevant to my needs?**
2. **Do I satisfy their eligibility requirements?**
3. **Can I potentially benefit from multiple schemes together?**
4. **What documents and next steps are required?**

### Our Core Philosophy
**Need → Eligibility → Verified Schemes → Action Plan**

The platform does not promise government approval. It helps farmers understand potential eligibility and navigate official application channels with complete clarity.

---

## ⚡ 3. What Makes YojanaSaathi Innovative?

### Innovation 01 — Three-State Deterministic Eligibility Engine
YojanaSaathi evaluates individual eligibility conditions using three explicit states:
- **`PASS`**: The available evidence satisfies the condition.
- **`FAIL`**: The available evidence contradicts the condition.
- **`UNKNOWN`**: Information is missing, insufficient, or unverified. Missing data is **never** assumed to be `PASS`.

### Innovation 02 — Conversational Hindi Intake & Bigha Ambiguity Resolution
Farmers can type or speak in Hindi (e.g. *"मेरे पास दो बीघा जमीन है और मैं गेहूं की खेती करता हूं। मुझे सिंचाई के लिए सरकारी सहायता चाहिए।"*). The intake engine parses the intent, crops, and landholding, flags regional Bigha unit variations across UP, asks targeted follow-up questions, and transitions confirmed profiles into deterministic rules evaluation with one click.

### Innovation 03 — Pairwise Multi-Scheme Convergence Engine
Evaluates all $\binom{6}{2} = 15$ scheme pairs independently. Rejects false transitivity ($A \sim B \land B \sim C \not\implies A \sim C$). Every compatibility relationship cites published operational circulars or gazette notifications.

### Innovation 04 — 7-Stage Progressive Benefit Journey & Unified Deduplication
Visual journey tracking embedded in Action Plans. Shared documents (Aadhaar, Khatauni ROR, Bank Passbook) are deduplicated across portfolios, saving farmers multiple Tehsil visits.

### Innovation 05 — Low-Bandwidth Rural Resilience
Generated action plans are cached locally in the browser (`localStorage`), enabling farmers to review requirements and application steps even after cellular connectivity drops in village environments.

---

## 🏛️ 4. Active Government Schemes (Uttar Pradesh)

All 6 active schemes are verified against official Gazette notifications with 100% live government portal destinations:

1. **PM-KISAN:** Pradhan Mantri Kisan Samman Nidhi (`https://pmkisan.gov.in`)
2. **PMFBY:** Pradhan Mantri Fasal Bima Yojana (`https://pmfby.gov.in`)
3. **PMKSY-PDMC:** PM Krishi Sinchayee Yojana — Per Drop More Crop (`https://pmksy.gov.in`)
4. **KCC:** Kisan Credit Card Institutional Agricultural Credit (`https://www.myscheme.gov.in/schemes/kcc`)
5. **UP Krishak Durghatna:** UP Mukhyamantri Krishak Durghatna Kalyan Yojana (`https://edistrict.up.gov.in`)
6. **SMAM Machinery:** Sub-Mission on Agricultural Mechanization (`https://agrimachinery.nic.in`)

---

## 📚 5. Standardized Documentation Suite (`docs/`)

All engineering blueprints, policy matrices, test reports, and hackathon presentation guides are organized in the [`docs/`](./docs/) directory:

- 🏗️ **Architecture:**
  - [`docs/architecture/SYSTEM_ARCHITECTURE.md`](./docs/architecture/SYSTEM_ARCHITECTURE.md): Multi-tier decoupled architecture & engine topology.
  - [`docs/architecture/DATABASE_DESIGN.md`](./docs/architecture/DATABASE_DESIGN.md): PostgreSQL/SQLite dual-engine schema & indexing strategy.
- 🌾 **Product & Journeys:**
  - [`docs/product/PRODUCT_OVERVIEW.md`](./docs/product/PRODUCT_OVERVIEW.md): Problem statement, innovation, and rural feasibility analysis.
  - [`docs/product/USER_JOURNEYS.md`](./docs/product/USER_JOURNEYS.md): Detailed 7-stage progressive farmer benefit journey.
- 📜 **Policy Evidence & Matrices:**
  - [`docs/policy/POLICY_VERIFICATION_MATRIX.md`](./docs/policy/POLICY_VERIFICATION_MATRIX.md): Complete statutory gazette register for all 6 active schemes.
  - [`docs/policy/CONVERGENCE_EVIDENCE_MATRIX.md`](./docs/policy/CONVERGENCE_EVIDENCE_MATRIX.md): Independent pairwise compatibility evidence across all 15 pairs.
- 🛡️ **Security:**
  - [`docs/security/SECURITY_AUDIT.md`](./docs/security/SECURITY_AUDIT.md): Threat modeling, password hashing, JWT family rotation, and RBAC audit.
- 🧪 **Testing:**
  - [`docs/testing/TEST_STRATEGY.md`](./docs/testing/TEST_STRATEGY.md): Comprehensive test automation strategy and Playwright E2E spec.
  - [`docs/testing/TEST_RESULTS.md`](./docs/testing/TEST_RESULTS.md): Detailed test execution report (57/57 tests passing 100%).
- 🚀 **Deployment:**
  - [`docs/deployment/DEPLOYMENT_GUIDE.md`](./docs/deployment/DEPLOYMENT_GUIDE.md): Local, Docker, and Cloud production deployment instructions.
- 🔍 **Audits & Remediation:**
  - [`docs/audit/INITIAL_REPOSITORY_AUDIT.md`](./docs/audit/INITIAL_REPOSITORY_AUDIT.md): Pre-transformation baseline audit across 19 areas.
  - [`docs/audit/REPOSITORY_CLEANUP_REPORT.md`](./docs/audit/REPOSITORY_CLEANUP_REPORT.md): Safe cleanup, bloat reduction (>96%), and exclusion report.
  - [`docs/audit/FINAL_ENGINEERING_AUDIT.md`](./docs/audit/FINAL_ENGINEERING_AUDIT.md): Independent post-remediation engineering audit.
- 🏆 **Hackathon Submission:**
  - [`docs/submission/HACKATHON_DEMO_SCRIPT.md`](./docs/submission/HACKATHON_DEMO_SCRIPT.md): 5-minute live winning demo script.
  - [`docs/submission/FEATURE_SHOWCASE.md`](./docs/submission/FEATURE_SHOWCASE.md): Platform capability highlights and UX features.
  - [`docs/submission/TECHNICAL_DIFFERENTIATORS.md`](./docs/submission/TECHNICAL_DIFFERENTIATORS.md): Deep-dive comparisons vs generic chatbots.
  - [`docs/submission/KNOWN_LIMITATIONS.md`](./docs/submission/KNOWN_LIMITATIONS.md): Transparent disclosures, non-claims, and future roadmap.
  - [`docs/submission/FINAL_SUBMISSION_CHECKLIST.md`](./docs/submission/FINAL_SUBMISSION_CHECKLIST.md): Signed submission readiness checklist.

---

## 🚀 6. Running the Project Locally

### Step 1 — Clone Repository
```bash
git clone https://github.com/arorautkarsh05-web/YojanaSaathi-AI.git
cd YojanaSaathi-AI
```

### Step 2 — Backend Setup
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r backend/requirements.txt
alembic -c backend/alembic.ini upgrade head
python -c "import sys; sys.path.insert(0, 'backend'); from app.db.session import SessionLocal; from app.services.scheme_seeder import seed_schemes_and_rules; db=SessionLocal(); seed_schemes_and_rules(db); db.close()"
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
Interactive API Docs: `http://127.0.0.1:8000/docs`

### Step 3 — Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open Frontend: `http://localhost:5173`

### Step 4 — Run Automated Test Suite
```bash
pytest backend/tests -v
```

---

## 🐳 7. Docker Deployment (Single Command)
```bash
cp .env.example .env
docker-compose up -d --build
```

---

## ⚠️ 8. Important Statutory Disclaimer

YojanaSaathi AI is an independent farmer welfare intelligence and preparation platform. It is not an official government portal and does not represent any government department. Eligibility assessments are informational and do not guarantee application acceptance, benefit disbursement, or sovereign government approval. Final eligibility and benefit disbursement remain subject to statutory verification by the respective government authority.

---

## ❤️ Built With Purpose
**YojanaSaathi AI — Technology with agricultural dignity, transparency, and trust.**  
*Built with ❤️ for the Farmers of Uttar Pradesh by **Team Aalekh** (Adima Agarwal, Utkarsh Arora)*
