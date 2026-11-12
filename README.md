# YojanaSaathi AI (योजना साथी AI)
> **Evidence-Grounded Farmer Benefit Intelligence & Multi-Scheme Convergence Platform**  
> *Initial Geography: Uttar Pradesh (75 Districts) | Multilingual: हिन्दी, English, Hinglish, ਪੰਜਾਬੀ*

### 👥 Team Information
- **Team Name:** Aalekh
- **Team Members:**
  - **Adima Agarwal** (Team Leader)
  - **Utkarsh Arora**

[![Tests](https://img.shields.io/badge/Pytest-41%20Passed-brightgreen)](file:///d:/YojanaSaathi/backend/tests)
[![Frontend](https://img.shields.io/badge/Vite%20React%2019-Production%20Ready-blue)](file:///d:/YojanaSaathi/frontend)
[![DPDP Act 2023](https://img.shields.io/badge/Compliance-DPDP%20Act%202023%20Data%20Minimization-success)](file:///d:/YojanaSaathi/documentation/SECURITY_MEASURES.md)
[![Portals](https://img.shields.io/badge/Statutory%20Portals-100%25%20Verified%20(200%20OK)-emerald)](file:///d:/YojanaSaathi/documentation/README.md)

---

## 📖 Complete Documentation Suite

All detailed system documentation, security specifications, feasibility assessments, competitive comparisons, and innovations are consolidated in the [`documentation/`](./documentation/) directory:

- 🛡️ [**Security Measures (`documentation/SECURITY_MEASURES.md`)**](./documentation/SECURITY_MEASURES.md): Dual-token architecture, Token Replay Attack Detection, Session Family Revocation, DPDP Act 2023 Compliance, and Data Minimization.
- 📊 [**Feasibility Study (`documentation/FEASIBILITY.md`)**](./documentation/FEASIBILITY.md): Technical bandwidth resilience, low-latency execution (<35ms), economic viability (zero LLM overhead), and UP operational alignment.
- ⚡ [**Competitive Differentiation (`documentation/DIFFERENTIATION.md`)**](./documentation/DIFFERENTIATION.md): How YojanaSaathi fundamentally differs from generic portals (myscheme.gov.in), hallucinating AI chatbots (ChatGPT), and commercial FinTech calculators.
- 💡 [**Core Innovations (`documentation/INNOVATION.md`)**](./documentation/INNOVATION.md): 4-Stage Transparent Farmer Journey, Grounded Multilingual Assistant, Pairwise Convergence Matrix, and Unified Document Deduplication.
- 📑 [**Technical Architecture Guide (`documentation/README.md`)**](./documentation/README.md): Detailed API contracts, database schema, gazette citations, and deployment guides.
- 🗄️ [**Audits Archive (`documentation/audits/`)**](./documentation/audits/): 25 comprehensive engineering audit reports covering policy accuracy, database compatibility, frontend functional QA, and production readiness.

---

## 🌾 The 4-Stage Transparent Farmer Journey

$$\text{1. खेती की ज़रूरत (Need)} \longrightarrow \text{2. पात्रता नियम (Eligibility)} \longrightarrow \text{3. सत्यापित योजनाएँ (Schemes)} \longrightarrow \text{4. कार्य योजना (Action Plan)}$$

1. **Need Identification:** Farmers declare actual requirements (income aid, crop damage relief, micro-irrigation, credit, farm implements).
2. **Deterministic Eligibility Rules:** Every criterion is evaluated using strict 3-state logic (`PASS`, `FAIL`, `UNKNOWN`) against official gazettes.
3. **Multi-Scheme Convergence:** Automatically checks whether multiple schemes can be availed simultaneously without double-claiming.
4. **Actionable Roadmap:** Outputs a consolidated, deduplicated document checklist, deadline countdowns (e.g. 72-hour crop loss intimation), and clickable links to official government portals.

---

## 🏛️ Supported Uttar Pradesh Schemes (100% Grounded)

All schemes link strictly to verified, live (`HTTP 200 OK`) official destinations:
- **PM-KISAN (Pradhan Mantri Kisan Samman Nidhi):** ₹6,000/yr cash aid ([pmkisan.gov.in](https://pmkisan.gov.in))
- **PMFBY (Pradhan Mantri Fasal Bima Yojana):** Crop insurance with 1.5%/2% premiums and strict 72-hr loss intimation ([pmfby.gov.in](https://pmfby.gov.in))
- **PMKSY-PDMC (Micro-Irrigation):** 55% subsidy on Drip and Sprinklers for small/marginal farmers ([uphorticulture.gov.in](https://uphorticulture.gov.in))
- **KCC (Kisan Credit Card):** Up to ₹3 Lakh at 4% effective interest ([myscheme.gov.in/schemes/kcc](https://www.myscheme.gov.in/schemes/kcc))
- **UP Krishak Durghatna Kalyan Yojana:** Up to ₹5 Lakh one-time accidental relief ([edistrict.up.gov.in](https://edistrict.up.gov.in))
- **SMAM Machinery:** 40%–50% subsidy on modern farm implements ([agriculture.up.gov.in](https://agriculture.up.gov.in))

---

## 🚀 Running the Project Locally

### 1. Backend Server
```bash
# Activate virtual environment
venv\Scripts\activate   # Linux/Mac: source venv/bin/activate

# Run all 41 automated tests
venv\Scripts\pytest backend\tests -v

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload
```
Interactive Swagger API Documentation: `http://127.0.0.1:8000/docs`

### 2. Frontend Application
```bash
# In frontend directory
cd frontend
npm install

# Start Vite dev server on port 5173
npm run dev

# Or build production bundle
npm run build
```
Web Application URL: `http://localhost:5173`

---

## 🔒 Security & Privacy Guarantees
- **No Aadhaar Numbers Stored:** We verify eligibility without ever ingesting or storing 12-digit UID numbers.
- **Full Guest Mode:** Farmers can discover schemes and generate Action Plans without creating an account or providing phone numbers.
- **Token Replay Defense:** Stolen refresh tokens trigger automatic session family revocation.
- **DPDP Act 2023 Compliant:** Full support for Right to Erasure (`DELETE /api/v1/auth/me/data`) and Data Portability (`GET /api/v1/auth/me/export`).

---

*Built with agricultural dignity, editorial precision, and anti-hallucination engineering.*
