# YojanaSaathi AI — Technical & System Documentation
> **Evidence-Grounded Farmer Benefit Intelligence & Multi-Scheme Convergence Platform**  
> Initial Geography: Uttar Pradesh, India | Target Users: Farmers, Farmer Families, Assistance Workers

### 👥 Team Information
- **Team Name:** Aalekh
- **Team Members:**
  - **Adima Agarwal** (Team Leader)
  - **Utkarsh Arora**

---

## 1. Executive Summary

**YojanaSaathi AI** is a production-grade digital platform designed to bridge the gap between Indian agricultural families and government welfare schemes. Unlike generic scheme portals that present static text or ungrounded AI chatbots that fabricate eligibility and deadlines, YojanaSaathi operates as an **evidence-based preparation, decision-support, and multi-scheme convergence engine**.

### Core Problem It Solves
1. **Fragmented Portals:** Farmers in Uttar Pradesh must navigate dozens of disconnected portals (`pmkisan.gov.in`, `pmfby.gov.in`, `edistrict.up.gov.in`, `agriculture.up.gov.in`).
2. **Exclusion Errors:** Farmers miss benefits due to misunderstandings of statutory exclusions (e.g., income-tax paying criteria, institutional landholder rules).
3. **Lapsed Deadlines:** Lack of awareness regarding statutory timelines (e.g., the strict 72-hour crop loss intimation deadline in PMFBY or 45-day accidental claim submission in UP Krishak Durghatna).
4. **Subsidies Duplication Confusion:** Farmers lack clarity on whether availing one scheme (e.g., PM-KISAN) disqualifies them from subsidized credit (KCC) or crop insurance (PMFBY).

---

## 2. Platform Architecture

```
                                  [ Farmer / Assistance Worker UI ]
                               (React 19 + Vite + Tailwind CSS)
                                              |
                          REST API / JSON (with Auth & CSRF tokens)
                                              |
                                              v
                               [ FastAPI Backend Service ]
                                (Python 3.13 / Uvicorn)
                                              |
     +--------------------+-------------------+--------------------+--------------------+
     |                    |                   |                    |                    |
     v                    v                   v                    v                    v
[ Eligibility Engine ] [ Convergence ] [ Document Deduplication ] [ Grounded QA ] [ Auth & Security ]
  (Deterministic        (Pairwise         (Unified Checklist       (Multilingual      (JWT + Replay
   Rule Evaluation)      Compatibility)    & Action Plan)           Assistant)         Revocation)
     |                    |                   |                    |                    |
     +--------------------+-------------------+--------------------+--------------------+
                                              |
                                              v
                                [ PostgreSQL / SQLite ORM ]
                            (Alembic Migrations + DPDP Vault)
```

---

## 3. Supported Schemes (Uttar Pradesh Baseline)

All schemes are mapped to published gazette notifications with verification timestamps:

1. **PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)**
   - *Authority:* Ministry of Agriculture & Farmers Welfare, GoI / UP Dept of Agriculture
   - *Benefit:* ₹6,000/year direct cash transfer in 3 equal installments of ₹2,000 via Aadhaar DBT.
   - *Statutory Source:* PM-KISAN Operational Guidelines 2020 (Clause 2.1 & Clause 3).
   - *Portal:* `https://pmkisan.gov.in`

2. **PMFBY (Pradhan Mantri Fasal Bima Yojana - UP)**
   - *Authority:* Dept of Agriculture, Govt of Uttar Pradesh / MoA&FW
   - *Benefit:* Subsidized crop insurance (1.5% Rabi, 2% Kharif premium) with full non-preventable natural disaster compensation.
   - *Statutory Source:* PMFBY Revised Operational Guidelines 2023 (Sec 4.1 & 6).
   - *Portal:* `https://pmfby.gov.in`

3. **PMKSY-PDMC (Per Drop More Crop - Drip & Sprinkler Micro-Irrigation)**
   - *Authority:* Department of Horticulture & Food Processing, Govt of Uttar Pradesh
   - *Benefit:* 55% capital subsidy for small/marginal farmers (<= 5 acres) and 45% for other farmers.
   - *Statutory Source:* PMKSY Guidelines Clause 4.2 & UP Govt Order No. 112/Hort/2023.
   - *Portal:* `https://uphorticulture.gov.in` & `https://pmksy.gov.in`

4. **KCC (Kisan Credit Card Institutional Farm Credit)**
   - *Authority:* Dept of Agriculture & Farmers Welfare / RBI / NABARD
   - *Benefit:* Concessional production credit up to ₹3,00,000 at 4% effective annual interest (with 3% prompt repayment subvention); collateral-free up to ₹1,60,000.
   - *Statutory Source:* RBI Master Circular FIDD.CO.FSD.BC.No.6/2022-23.
   - *Portal:* `https://www.myscheme.gov.in/schemes/kcc` & `https://fasalrin.gov.in`

5. **UP Mukhyamantri Krishak Durghatna Kalyan Yojana**
   - *Authority:* Revenue Department, Govt of Uttar Pradesh
   - *Benefit:* Up to ₹5,00,000 one-time ex-gratia relief for accidental death or permanent 100% disability (Age 18–70). *Explicitly clarified as one-time assistance, not an ongoing pension.*
   - *Statutory Source:* UP Revenue Dept Notification No. 1420/1-11-2020-04(01)/2020.
   - *Portal:* `https://edistrict.up.gov.in` & `https://bor.up.gov.in`

6. **SMAM Machinery (Sub-Mission on Agricultural Mechanization)**
   - *Authority:* Department of Agriculture, Govt of Uttar Pradesh
   - *Benefit:* 40% to 50% subsidy on modern implements (Rotavators, Laser Levelers) and up to ₹4 Lakh for Custom Hiring Centres.
   - *Statutory Source:* SMAM Guidelines Chapter III & UP DBT Circular 2024.
   - *Portal:* `https://agriculture.up.gov.in` & `https://agrimachinery.nic.in`

---

## 4. Documentation Suite Index

| Document | Purpose & Key Topics |
| :--- | :--- |
| [**SECURITY_MEASURES.md**](./SECURITY_MEASURES.md) | Authentication architecture, token replay protection, session family revocation, DPDP Act 2023 privacy compliance, guest mode data minimization, audit logging. |
| [**FEASIBILITY.md**](./FEASIBILITY.md) | Technical, operational, economic, infrastructure, and field deployment feasibility across Uttar Pradesh's 75 districts. |
| [**DIFFERENTIATION.md**](./DIFFERENTIATION.md) | How YojanaSaathi fundamentally differs from generic chatbots, static government registries, and basic single-scheme calculators. |
| [**INNOVATION.md**](./INNOVATION.md) | Key architectural, product, linguistic, and user experience innovations powering the platform. |

---

## 5. Quickstart & Local Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- Git

### Backend Setup
```bash
# Navigate to backend and activate virtualenv
cd backend
python -m venv venv
venv\Scripts\activate   # Windows: venv\Scripts\activate, Linux/Mac: source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and seed catalogue
python -c "from app.services.scheme_seeder import seed_schemes; from app.db.session import SessionLocal; db = SessionLocal(); seed_schemes(db); db.close()"

# Start API server with live reloader
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at `http://127.0.0.1:8000/docs`.

### Frontend Setup
```bash
# Navigate to frontend
cd frontend
npm install

# Start Vite dev server
npm run dev
```
Client application will be accessible at `http://localhost:5173`.

### Automated Testing
```bash
# Run complete test suite (41 unit and integration tests)
venv\Scripts\pytest backend\tests -v
```

