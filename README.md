# 🌾 YojanaSaathi AI (योजना साथी AI)

### Evidence-Grounded Farmer Benefit Intelligence & Multi-Scheme Convergence Platform

**Bridging the gap between farmers and government welfare through transparent, explainable, and evidence-driven technology.**

YojanaSaathi AI is an intelligent farmer-benefit navigation platform designed to simplify access to agricultural and rural welfare schemes. It helps farmers discover potentially applicable government schemes, understand eligibility conditions, identify missing information, explore multi-scheme convergence opportunities, prepare documents, and navigate official application channels through a transparent seven-stage journey.

**Our core philosophy: AI understands the farmer. Deterministic engines evaluate eligibility. Official policy evidence establishes trust. One unified action plan guides the next step.**

---

## 👥 Team Aalekh (टीम आलेख)

| Team Member | Role | Organization |
|---|---|---|
| **Adima Agarwal** | Team Leader | Team Aalekh |
| **Utkarsh Arora** | Team Member | Team Aalekh |

---

## 📊 Project at a Glance

| Category | Details |
|---|---|
| Project | YojanaSaathi AI |
| Domain | AgriTech / GovTech / Social Impact |
| Primary Users | Farmers and rural communities |
| Initial Geography | Uttar Pradesh, India |
| Geographic Coverage | 75 Districts of Uttar Pradesh |
| Scheme Coverage | 6 agricultural and farmer-welfare schemes |
| Eligibility Architecture | Deterministic Three-Valued Logic |
| Convergence Architecture | Evidence-Based Pairwise Analysis |
| User Experience | Seven-Stage Farmer Benefit Journey |
| Backend | FastAPI / Python |
| Frontend | React 19 / Vite / Tailwind CSS |
| Testing | Pytest + Playwright |
| Database | SQLite / PostgreSQL support |

### Implementation & Testing Indicators
<img width="1882" height="907" alt="image" src="https://github.com/user-attachments/assets/2328bf50-f05b-4b0c-98e1-8a387e40dadd" />



[![Tests](https://img.shields.io/badge/Pytest-105%20Passed-brightgreen.svg)](documentation/README.md)
[![Playwright](https://img.shields.io/badge/Playwright-7%20Milestones-blueviolet.svg)](documentation/README.md)
[![Convergence](https://img.shields.io/badge/Convergence-15%20Pairs%20Evaluated-darkgreen.svg)](documentation/INNOVATION.md)
[![Frontend](https://img.shields.io/badge/Frontend-React%2019%20%7C%20Vite-blue.svg)](frontend/)
[![Architecture](https://img.shields.io/badge/Eligibility-3--Valued%20Logic-success.svg)](documentation/INNOVATION.md)
[![Geography](https://img.shields.io/badge/UP%20Coverage-75%20Districts-orange.svg)](data/district_metadata/up_districts.json)

*Testing indicators reflect the project's reported test results. Run the test suite locally to reproduce them.*

---

# 1. 🚨 The Problem: Finding a Scheme Is Not the Same as Receiving a Benefit

India has multiple agricultural and farmer-welfare schemes, but discovering and accessing them can be difficult for farmers.

The problem is not simply a lack of information. It is the fragmentation of the entire benefit-access journey.

### Five Major Challenges

**1. Scheme Discovery Fragmentation**

Farmers often need to navigate multiple portals, departments, and information sources to discover schemes relevant to their circumstances.

**2. Complex Eligibility Conditions**

Eligibility may depend on landholding, crop, location, farmer category, income, bank details, exclusions, and other scheme-specific conditions.

**3. Missing or Incomplete Documentation**

A farmer may appear eligible but still be unable to proceed because required documents are missing, outdated, or incorrectly prepared.

**4. Missed Multi-Scheme Opportunities**

Farmers may not know whether multiple schemes can be accessed together or whether specific combinations have restrictions.

**5. Lack of End-to-End Guidance**

Finding a scheme does not automatically explain what to do next, where to apply, which documents to prepare, or how to track application progress.

### The Core Problem

**Farmers need more than another scheme-information portal. They need a transparent system that connects their circumstances with policy-backed eligibility assessment, document readiness, and actionable application guidance.**

---

# 2. 💡 Our Solution: YojanaSaathi AI

YojanaSaathi AI transforms fragmented scheme information into a structured farmer-benefit action plan.

Instead of simply displaying scheme descriptions, it connects five important capabilities:

| Capability | What It Does |
|---|---|
| Intelligent Farmer Intake | Understands farmer information through a guided, accessible interface. |
| Eligibility Intelligence | Evaluates scheme conditions using deterministic rules and three-valued logic. |
| Multi-Scheme Convergence | Evaluates potential compatibility between selected schemes using pairwise relationships. |
| Document Readiness | Identifies required documents and helps organize the preparation process. |
| Action Plan & Progress | Guides farmers towards official application channels and tracks reported progress. |

### What Makes the Approach Different?

Traditional information discovery answers:

*"Which schemes are available?"*

YojanaSaathi AI aims to answer:

- Which schemes may apply to this farmer?
- Why does the farmer appear eligible or ineligible?
- What information is still missing?
- Which documents are required?
- Which schemes may work together?
- What should the farmer do next?
- What is the current application or benefit status?

---

# 3. 🚀 Core Innovations
<img width="1885" height="891" alt="image" src="https://github.com/user-attachments/assets/030cc9b7-fcd3-4bec-918c-04b2cfa79903" />


## Innovation 1: Explainable Three-Valued Eligibility Engine

Most basic eligibility systems rely on binary decisions:

- Eligible
- Not Eligible

However, real-world scheme eligibility often involves incomplete information.

YojanaSaathi AI uses deterministic three-valued logic:

| Result | Meaning |
|---|---|
| `PASS` | Available evidence satisfies the evaluated condition. |
| `FAIL` | Available evidence contradicts the evaluated condition. |
| `UNKNOWN` | Information is missing, ambiguous, or insufficient to establish a result. |

### Why Is This Important?

Consider a farmer whose landholding information is incomplete.

A conventional binary system may incorrectly classify the farmer.

YojanaSaathi AI can return:

`UNKNOWN — Landholding details require clarification.`

This avoids presenting uncertainty as a confirmed rejection or approval.

**Innovation:** Eligibility assessment becomes explainable, traceable, and uncertainty-aware rather than relying on unsupported AI-generated conclusions.

## Innovation 2: Evidence-Based Multi-Scheme Convergence Engine

Farmers may qualify for more than one welfare programme.

However, compatibility cannot safely be assumed simply because two schemes address different needs.

YojanaSaathi AI evaluates scheme combinations through pairwise relationships.

For six schemes:

\[
\binom{6}{2}=\frac{6(5)}{2}=15
\]

This creates 15 unique scheme pairs for evaluation.

Each relationship is assigned an evidence-aware status, such as:

- `COMPATIBLE_CONFIRMED`
- `INCOMPATIBLE_CONFIRMED`
- `UNKNOWN_REQUIRES_VERIFICATION`

### Anti-Transitivity Protection

If Scheme A is compatible with Scheme B, and Scheme B is compatible with Scheme C, the system does not automatically assume that Scheme A is compatible with Scheme C.

Every pair must be evaluated independently.

**Innovation:** Multi-scheme discovery is treated as a policy-evidence problem rather than a simple recommendation or combination exercise.

## Innovation 3: Uttar Pradesh Bigha Ambiguity Resolution

Land measurements can vary across regions.

In Uttar Pradesh, interpreting a farmer's reported landholding without understanding the local measurement convention can create incorrect eligibility calculations.

YojanaSaathi AI incorporates regional land-unit clarification, including the distinction between Pucca and Kachha Bigha where supported by the configured regional data.

Instead of blindly converting a farmer's input, the system can request clarification.

**Innovation:** Local measurement ambiguity is treated as an eligibility-critical data-quality issue.

## Innovation 4: Unified Document Readiness

Farmers may need to prepare overlapping documents for multiple schemes.

YojanaSaathi AI introduces a unified document-readiness approach that aims to:

- Identify scheme-specific document requirements.
- Avoid unnecessary duplicate uploads.
- Track document preparation.
- Display pending and completed requirements.
- Support document verification workflows.

Document upload and verification are treated as separate states.

A successful upload does not automatically mean that a document has been officially verified.

Aadhaar is required only where the applicable scheme rules and legal requirements establish that it is necessary.

## Innovation 5: Seven-Stage Transparent Farmer Benefit Journey

YojanaSaathi AI connects the complete farmer experience through a structured seven-stage workflow.

| Stage | Journey | Purpose |
|---|---|---|
| 1 | Farmer Profile | Capture farmer information. |
| 2 | Eligibility Assessment | Evaluate applicable scheme conditions. |
| 3 | Missing Information | Resolve incomplete or ambiguous inputs. |
| 4 | Document Verification | Prepare and track required documents. |
| 5 | Official Application | Guide farmers towards official application channels. |
| 6 | Farmer Progress | Track farmer-reported application progress. |
| 7 | Benefit Status | Distinguish reported progress from verified government outcomes. |

### Transparency by Design

The system explicitly distinguishes between:

- Preliminary eligibility.
- Document readiness.
- Farmer-reported application completion.
- Government-verified application status.
- Benefit sanction.
- Benefit disbursement.

**Innovation:** A farmer's reported progress is never automatically represented as government approval or confirmed benefit disbursement.

## Innovation 6: Offline-Resilient Farmer Experience

Rural connectivity can be inconsistent.

YojanaSaathi AI incorporates offline-recovery functionality for supported application data and action-plan information.

The objective is to help farmers revisit previously prepared information when connectivity is interrupted.

Offline availability does not mean that government portals, live verification, or online application submission remain operational without an internet connection.

---

# 4. ⚖️ How Is YojanaSaathi AI Different from Existing Platforms?
<img width="1882" height="902" alt="image" src="https://github.com/user-attachments/assets/d711962b-7255-4b1b-8229-b7908d4289d6" />


YojanaSaathi AI is not designed to replace government portals or existing farmer-support services.

It is designed to complement them by connecting scheme discovery, explainable assessment, document readiness, and application navigation.

| Capability | Government Scheme Information Portals | General-Purpose AI Chatbots | YojanaSaathi AI |
|---|---|---|---|
| Scheme Information | Yes | Can explain available information | Integrated scheme catalogue |
| Farmer-Centred Intake | Varies by platform | Conversational | Structured farmer-focused intake |
| Deterministic Eligibility Evaluation | Depends on portal | Not inherently guaranteed | Three-valued rule engine |
| Explainable Eligibility Results | Varies | Depends on response quality | PASS / FAIL / UNKNOWN |
| Missing Information Detection | Varies | Possible through conversation | Structured information-gap handling |
| Multi-Scheme Pairwise Analysis | Not the primary focus of many portals | No guaranteed policy validation | Dedicated convergence engine |
| Regional Land-Unit Clarification | Varies | May require prompting | Uttar Pradesh-focused clarification |
| Unified Document Readiness | Varies | Not a complete workflow | Document preparation and tracking |
| Seven-Stage Farmer Journey | Varies | Not inherently available | Integrated journey tracker |
| Official Application Navigation | Government portal-specific | Can provide guidance | Scheme-linked next-step guidance |
| Progress Transparency | Depends on integration | Cannot independently verify | Farmer-reported vs government-verified distinction |

### Our Differentiation

**1. From Information to Action**

We do not stop at displaying scheme descriptions. We connect recommendations to a structured action plan.

**2. From Generic AI Answers to Deterministic Assessment**

The eligibility core uses explicit rules and uncertainty-aware results instead of relying on generated text as the final decision-maker.

**3. From Individual Schemes to Convergence Intelligence**

The platform evaluates scheme relationships pair by pair instead of assuming that all benefits can be combined.

**4. From Static Checklists to Document Readiness**

The platform connects document requirements with the farmer's selected schemes and preparation journey.

**5. From Unclear Progress to Transparent Status**

The platform separates farmer-reported progress from independently verified government outcomes.

**Our positioning: YojanaSaathi AI is a farmer-benefit intelligence and application-navigation layer that complements existing official services.**

---

# 5. 🌱 Supported Scheme Ecosystem

The initial implementation focuses on six agricultural and farmer-welfare schemes.

| Scheme | Primary Focus |
|---|---|
| PM-KISAN | Income support for eligible farmer families |
| PMFBY | Crop insurance and notified crop-risk protection |
| Kisan Credit Card (KCC) | Institutional agricultural credit |
| PMKSY-PDMC | Per Drop More Crop / micro-irrigation |
| SMAM | Sub-Mission on Agricultural Mechanization |
| UP Mukhyamantri Krishak Durghatna Kalyan Yojana | Farmer and eligible family accident-related assistance |

The scheme catalogue is designed to support:

- Scheme-specific eligibility conditions.
- Required information.
- Document requirements.
- Official source references.
- Policy provenance.
- Convergence relationships.
- Uncertainty handling.

**Important:** A scheme recommendation is not a guarantee of eligibility, application acceptance, sanction, or payment. Actual decisions rest with the competent authorities.

---

# 6. 🏗️ System Architecture

YojanaSaathi AI follows a layered architecture that separates farmer interaction, deterministic policy evaluation, evidence management, and application guidance.

### High-Level Architecture

```text
              FARMER / CITIZEN
                     |
                     v
          React 19 + Vite Frontend
                     |
                     v
          Farmer Intake & Profile
                     |
                     v
           FastAPI Backend Layer
                     |
          +----------+-----------+
          |          |           |
          v          v           v
      Eligibility  Document   Scheme Catalogue
       Engine      Readiness   & Policy Evidence
          |          |           |
          v          v           v
      PASS / FAIL  Document   Source & Version
      / UNKNOWN    Tracking    References
          |          |           |
          +----------+-----------+
                     |
                     v
          Multi-Scheme Convergence
                     |
                     v
           Unified Action Plan
                     |
          +----------+-----------+
          |          |           |
          v          v           v
      Official    Farmer      Benefit Status
      Next Steps  Progress    Transparency
          |          |           |
          +----------+-----------+
                     |
                     v
            Farmer Summary PDF
```

### Architectural Principles

- Deterministic eligibility evaluation.
- Evidence-aware policy records.
- Explainable decisions.
- Explicit uncertainty handling.
- Pairwise scheme compatibility.
- Separation of AI assistance and statutory decisions.
- Secure handling of farmer information.
- Traceable state transitions.

---

# 7. 🔐 Privacy, Security & Trust

Farmer data may contain sensitive identity, banking, and landholding information.

YojanaSaathi AI follows a privacy-conscious architecture.

### Security Measures

- Authentication and role-based access control.
- Password hashing.
- Secure token handling and refresh-token protections.
- Server-side input validation.
- Parameterized database operations.
- Secure document-upload validation.
- File-type and file-content validation.
- Access-controlled document storage.
- Audit logging for sensitive operations.
- Aadhaar masking where applicable.
- Protection against unauthorized cross-user document access.

### Trust Principles

1. Uploaded documents are not automatically treated as verified.
2. Missing information is represented explicitly.
3. Scheme recommendations retain their evidence context.
4. Farmer-reported progress is not represented as government-confirmed status.
5. Official approval and benefit disbursement remain the responsibility of competent authorities.

---

# 8. 🧪 Testing & Quality Assurance

Testing is an important part of the platform's development.

### Backend Testing

The project reports 105 passing Pytest tests covering areas such as:

- Eligibility evaluation.
- Three-valued logic.
- Scheme policy records.
- Multi-scheme convergence.
- Document requirements.
- API behaviour.
- Security-related validation.
- Farmer journey workflows.

Run the backend suite locally:

```bash
pytest backend/tests/ -v
```

### Playwright End-to-End Testing

The project includes browser automation for the seven-stage farmer journey.

Reported milestones include:

1. Landing Page.
2. Farmer Assistant.
3. Farmer Intake.
4. Eligibility Evaluation.
5. Multi-Scheme Convergence.
6. Action Plan.
7. Offline Recovery.

Run:

```bash
python scripts/run_playwright_e2e.py
```

### Frontend Production Build

```bash
cd frontend
npm run build
```

For reproducibility, use the dependency lockfile and the documented environment requirements.

Detailed test instructions and evidence:

[Technical Documentation](documentation/README.md)

---

# 9. 📚 Complete Project Documentation

The `documentation/` directory contains the project's technical, innovation, security, and feasibility reports.

| Document | Description |
|---|---|
| [Master Technical Documentation](documentation/README.md) | Architecture, setup, APIs, system workflow, testing, and implementation details. |
| [Innovation Report](documentation/INNOVATION.md) | Three-valued eligibility logic, pairwise convergence, regional land-unit clarification, and offline recovery. |
| [Differentiation Report](documentation/DIFFERENTIATION.md) | Product positioning and comparison with existing approaches. |
| [Feasibility Report](documentation/FEASIBILITY.md) | Technical, operational, and financial feasibility assumptions. |
| [Security Measures](documentation/SECURITY_MEASURES.md) | Security architecture, data protection, and implementation controls. |

---

# 10. 🚀 Quick Start Guide

## Prerequisites

- Python 3.13+
- Node.js and npm
- Git

Use the dependency versions specified by the project.

### Step 1: Clone the Repository

```bash
git clone https://github.com/arorautkarsh05-web/YojanaSaathi-AI.git

cd YojanaSaathi-AI
```

### Step 2: Backend Setup

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
venv\Scripts\Activate.ps1
```

Install backend dependencies:

```bash
pip install -r backend/requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --app-dir backend --reload --port 8000
```

Backend API:

`http://127.0.0.1:8000`

Interactive API documentation:

`http://127.0.0.1:8000/docs`

### Step 3: Frontend Setup

Open another terminal:

```bash
cd frontend

npm install

npm run dev
```

Open:

`http://localhost:5173`

### Step 4: Run Backend Tests

From the project root:

```bash
pytest backend/tests/ -v
```

### Step 5: Run Browser Automation

```bash
python scripts/run_playwright_e2e.py
```

---

# 11. 🗺️ Project Roadmap

YojanaSaathi AI is designed as an extensible platform.

Potential future improvements include:

- Expansion beyond Uttar Pradesh.
- Additional verified government schemes.
- More regional language support.
- Voice-first farmer interaction.
- Assisted document classification.
- Improved low-connectivity experiences.
- Authorized government-service integrations.
- Application acknowledgement tracking.
- Verified application-status integrations.
- Accessibility improvements for low-literacy users.
- CSC and assisted-service-centre workflows.

These are development directions, not claims of already deployed integrations.

---

# 12. 🎯 Expected Social Impact

YojanaSaathi AI aims to improve the accessibility and understandability of farmer-welfare information.

| Impact Area | Intended Outcome |
|---|---|
| Scheme Awareness | Help farmers discover potentially relevant schemes. |
| Eligibility Clarity | Explain why a scheme may or may not apply. |
| Reduced Confusion | Identify missing information before application. |
| Document Readiness | Organize supporting documents across schemes. |
| Benefit Convergence | Highlight potentially compatible scheme combinations. |
| Application Guidance | Provide clear next steps and official channels. |
| Transparency | Separate recommendations, reported progress, and verified outcomes. |

**The objective is not to promise benefits. It is to make the path towards accessing legitimate benefits clearer, more transparent, and easier to navigate.**

---

# 13. ⚖️ Important Disclaimer

YojanaSaathi AI is an independent technology project developed by Team Aalekh. It is not affiliated with, operated by, or officially endorsed by any government department.

The platform provides decision-support, scheme discovery, eligibility assessment, document preparation, and application-navigation assistance based on available policy information.

It does not independently grant eligibility, approve applications, issue government certificates, sanction benefits, or authorize payments.

Final eligibility, application acceptance, approval, sanction, and disbursement decisions rest solely with the competent government authorities.

Users should verify current scheme conditions, deadlines, and application requirements through the relevant official channels before applying.

---

## 🌾 Built with the Vision of Making Government Welfare More Accessible

**YojanaSaathi AI — क्योंकि सही जानकारी, सही समय पर, हर किसान तक पहुँचनी चाहिए।**

**Team Aalekh | India**
