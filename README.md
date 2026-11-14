# 🌾 YojanaSaathi AI (योजना साथी AI)

### Evidence-Grounded Farmer Benefit Intelligence & Multi-Scheme Convergence Platform
> **Bridging the gap between farmers and government welfare through transparent, explainable and evidence-driven technology.**

---

## 👥 Team Aalekh (टीम आलेख)

| Team Member | Role | Organization |
|---|---|---|
| **Adima Agarwal** | Team Leader | Team Aalekh |
| **Utkarsh Arora** | Team Member | Team Aalekh |

[![Tests](https://img.shields.io/badge/Pytest-105%20Passed%20(100%25)-brightgreen.svg)](documentation/README.md#12-installation-setup--automated-test-suite-105-tests)
[![Playwright E2E](https://img.shields.io/badge/Playwright%20E2E-7%20Milestones%20Verified-blueviolet.svg)](documentation/README.md#4-complete-7-stage-farmer-benefit-journey)
[![Convergence](https://img.shields.io/badge/Convergence-All%2015%20Pairs%20Verified-darkgreen.svg)](documentation/README.md#8-multi-scheme-pairwise-convergence-engine)
[![Frontend](https://img.shields.io/badge/Vite%20React%2019-Production%20Build%20Clean-blue.svg)](frontend/)
[![Architecture](https://img.shields.io/badge/Deterministic%20Core-3--Valued%20Logic-forest.svg)](documentation/INNOVATION.md)
[![Coverage](https://img.shields.io/badge/UP%20Geography-All%2075%20Districts-success.svg)](data/district_metadata/up_districts.json)

---

## 📚 Complete Project Documentation (`documentation/`)

All comprehensive project reports, architectural specs, and competition submissions are organized inside the [documentation](file:///d:/YojanaSaathi/documentation) directory:

1. 📖 **[documentation/README.md](file:///d:/YojanaSaathi/documentation/README.md)** — **Master Technical & System Documentation** (Complete Project Guide, 7-Stage Journey, 1-Click Verification, Architecture, APIs, Test Instructions).
2. 💡 **[documentation/INNOVATION.md](file:///d:/YojanaSaathi/documentation/INNOVATION.md)** — **Technological Innovations** (Deterministic 3-Valued Rules, 15 Pairwise Convergence Relations, UP Bigha Ambiguity Resolution, PWA Offline Recovery).
3. ⚔️ **[documentation/DIFFERENTIATION.md](file:///d:/YojanaSaathi/documentation/DIFFERENTIATION.md)** — **How YojanaSaathi is Different from Other Platforms** (Side-by-side comparison matrix vs myScheme, ChatGPT/LLMs, Kisan Call Center 1551, State portals).
4. 📈 **[documentation/FEASIBILITY.md](file:///d:/YojanaSaathi/documentation/FEASIBILITY.md)** — **Technical, Financial & Operational Feasibility** (Zero-LLM token costs, CSC VLE integration, ₹0.10/consultation unit economics).
5. 🛡️ **[documentation/SECURITY_MEASURES.md](file:///d:/YojanaSaathi/documentation/SECURITY_MEASURES.md)** — **Security & Data Protection Architecture** (DPDP Act 2023 Masking, Magic-Byte File Validation, Token Replay Revocation).

---

## 💡 What Makes YojanaSaathi AI Unique?

Unlike conventional scheme portals that display static text or generic AI chatbots that hallucinate fake subsidies, **YojanaSaathi AI operates as a trustworthy decision-support, document preparation, and multi-scheme convergence platform**:

- **Zero Hallucination:** Powered by a deterministic 3-valued mathematical engine (`PASS`, `FAIL`, `UNKNOWN`).
- **All 15 Convergence Pairs Audited ($\binom{6}{2}=15$):** Synergistic multi-scheme combinations with anti-transitivity guarantees and Bundelkhand incentives.
- **UP 75-District Bigha Disambiguation:** Resolves Western UP Pucca Bigha (~0.625 acres) vs Eastern UP Kachha Bigha (~0.21-0.33 acres) to prevent fatal disqualifications.
- **Document Verification Center:** 1-Click tick-box verification for standard documents and secure auto-verified upload for Photo & Aadhaar.
- **7-Stage Interactive Journey:** Guides farmers from initial intake to departmental DBT sanction.
- **Official 1-Page Summary PDF:** Generates a printable, vector-rendered summary for physical CSC submission.
- **PWA Dual-State Offline Recovery:** Action plans and verified checklists persist in local storage, functioning seamlessly without internet in rural fields.

---

## 🚀 Quick Start Guide

### 1. Backend Server (FastAPI + Python 3.13)
```bash
# Activate virtual environment
venv\Scripts\activate       # Windows PowerShell

# Install dependencies
pip install -r backend/requirements.txt

# Run backend
uvicorn app.main:app --app-dir backend --reload --port 8000
```
Interactive API docs available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Application (React 19 + Vite + Tailwind CSS)
```bash
cd frontend
npm install
npm run dev
```
Access the application at: `http://localhost:5173`

### 3. Run Automated Tests (105 Tests, 100% Pass Rate)
```bash
# Run Pytest suite
pytest backend/tests/ -v

# Run Playwright E2E browser automation
python scripts/run_playwright_e2e.py
```

---

### 🏛️ Statutory Disclaimer
*YojanaSaathi AI is an independent, evidence-grounded welfare intelligence platform developed by Team Aalekh. It is NOT an official government application or certificate. All scheme recommendations and preparation plans are derived strictly from published gazette rules, and official benefit sanction remains the sole discretion of the respective government authority.*
