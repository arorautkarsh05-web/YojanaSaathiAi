# YojanaSaathi AI — System Architecture & Engineering Blueprint

## 1. System Overview

**YojanaSaathi AI (योजना साथी AI)** is an Evidence-Grounded Farmer Benefit Intelligence and Multi-Scheme Convergence Platform engineered specifically for the 75 administrative districts of Uttar Pradesh, India.

Unlike conventional conversational chatbots that hallucinate entitlement conditions or provide probabilistic estimates, YojanaSaathi decouples conversational interaction from statutory decision-making:
- **Conversational Layer (NLP/Intake):** Conducts natural language intake, detects language (Hindi, English, Hinglish, Punjabi), extracts farm parameters, identifies missing details, resolves localized land unit ambiguities (e.g. Pucca vs. Kachha Bigha), and provides source-anchored explanations.
- **Deterministic Evaluation Layer (Core Engine):** Implements three-valued logic (`PASS`, `FAIL`, `UNKNOWN`) to independently evaluate statutory rules against farmer profiles.
- **Pairwise Convergence Engine:** Computes pairwise multi-scheme compatibility using direct statutory evidence without flawed transitive assumptions ($A \sim B \land B \sim C \not\implies A \sim C$).
- **Action Plan & Readiness Engine:** Deduplicates document requirements, groups shared proofs (e.g., Aadhaar, Khatauni ROR, Bank Passbook), and plots a 7-stage farmer benefit journey.

```mermaid
flowchart TD
    Farmer[Farmer / Facilitator] -->|Hindi / English / Voice / Text| Frontend[Vite React 19 Frontend\nWCAG 2.2 AA]
    
    subgraph Conversation_Layer [Conversational Layer]
        Frontend -->|Natural Language Intake| Intake[Farmer Intake Service\nAmbiguity Resolution]
        Frontend -->|Scheme Questions| Assistant[Grounded Q&A Service\nGazette Retrieval]
    end

    subgraph Deterministic_Engine [Deterministic Decision Core]
        Intake -->|Structured Profile| RulesEngine[Deterministic 3-Valued Rules Engine\nPASS / FAIL / UNKNOWN]
        RulesEngine --> GeoEngine[UP 75-District Geo Applicability\nAgro-Climatic Zones & Crops]
        RulesEngine --> ConvergenceEngine[Pairwise Convergence Engine\nNo False Transitivity]
        RulesEngine --> ReadinessEngine[Readiness & Deduplication Engine\nShared Document Identification]
    end

    subgraph Persistence [Data & Audit Layer]
        RulesEngine --> DB[(PostgreSQL / SQLite Dual Engine)]
        ConvergenceEngine --> DB
        Admin[Department Admin / Auditor] -->|Policy Amendment Simulation| ImpactEngine[Policy Impact Engine\nAudit Trail Logging]
        ImpactEngine --> DB
    end
```

---

## 2. Core Architectural Principles

### 2.1 Deterministic Three-Valued Logic
Eligibility is never decided by an LLM. Every statutory condition evaluates to:
- **`PASS`**: The profile meets or exceeds statutory requirements.
- **`FAIL`**: The profile fails a mandatory condition (e.g. landholding > 2 Ha for marginal subsidy, or resident outside UP).
- **`UNKNOWN`**: Crucial data is missing or ambiguous (e.g. unverified landholding unit, missing crop selection, or pending land record verification). Missing information is **never** assumed to be `PASS`.

### 2.2 Pairwise Independent Convergence
Convergence relationships between schemes (e.g. PM-KISAN with KCC, or PMFBY with PMKSY) are evaluated strictly in pairs ($N \times (N-1) / 2$). No scheme relationship is inferred by transitivity. Each relationship must cite an official government document, circular, or guideline clause.

### 2.3 Transparent Multi-Factor Ranking
Recommended schemes are prioritized using an auditable formula:
$$\text{Score} = 0.40 \times \text{NeedRelevance} + 0.35 \times \text{EligibilityScore} + 0.10 \times \text{GeoRelevance} + 0.15 \times \text{FreshnessScore}$$
Crucially, relevance score **never** elevates a scheme whose mandatory conditions evaluate to `FAIL`.

### 2.4 Strict Non-Claimant Distinction
The system maintains an absolute distinction between:
- **Citizen Preparation & Navigation:** What YojanaSaathi does (identifying eligibility, missing documents, and directing to official portals).
- **Statutory Claim Approval:** What only designated government authorities (e.g., Tehsildar, Agriculture Officer, Bank Branch Manager) can execute.

---

## 3. Technology Stack & Directory Topology

- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, i18next (Hindi, English, Hinglish, Punjabi).
- **Backend:** FastAPI (Python 3.13), Pydantic v2, SQLAlchemy 2.0 ORM, Alembic migrations, Uvicorn ASGI server.
- **Database:** Dual-compatible engine supporting SQLite (zero-config hackathon execution) and PostgreSQL (production deployment with connection pooling).
- **Security:** Passlib (bcrypt/Argon2) password hashing, JWT access tokens (short TTL), family-based refresh token rotation with SHA-256 storage, Role-Based Access Control (RBAC).

---
*YojanaSaathi AI Engineering Team — Architecture Reference v3.0*

