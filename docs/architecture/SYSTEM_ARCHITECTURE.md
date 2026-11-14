# YojanaSaathi AI — Detailed System Architecture & Component Interactions
**Document Version:** 3.0.0  
**Scope:** Distributed Multi-Tier Architecture, Layer Decoupling, and Observability  
**Lead Architect:** Principal Software Architect

---

## 1. Architectural Topology

YojanaSaathi AI is built on a clean multi-tiered architecture that strictly separates stateless client presentation, conversational natural language intake, deterministic statutory evaluation, and persistent audit storage:

```
[ Citizen Client / Web Browser / Mobile ]
               │
               ▼  HTTP/2 (HTTPS)
   [ Reverse Proxy / Vite Server ]
               │
               ▼  Reverse Proxy to Backend (:8000)
    [ FastAPI Application Core ]
         ├── Security & RBAC Middleware
         ├── Natural Language Intake Service (Ambiguity Engine)
         ├── Grounded Multilingual Q&A (Gazette Anchored)
         │
         ├── Deterministic 3-Valued Rules Engine (PASS/FAIL/UNKNOWN)
         ├── 75-District Geo-Applicability Engine (Agro-Climatic Zones)
         ├── Pairwise Multi-Scheme Convergence Engine (Zero Transitivity)
         └── Action Plan & Readiness Deduplication Engine
               │
               ▼  SQLAlchemy 2.0 ORM (Parameterized Queries)
     [ PostgreSQL / SQLite Dual Storage Engine ]
```

---

## 2. Component Decoupling & Responsibilities

### 2.1 Presentation Tier (Frontend)
- **Framework:** React 19 + TypeScript + Vite.
- **Styling & Accessibility:** Tailwind CSS utility architecture, WCAG 2.2 AA compliant contrast ratios, accessible form validation, and screen reader labels.
- **Resilience:** LocalStorage caching for generated action plans enabling offline viewing in low-connectivity rural belts of UP.

### 2.2 Service & Engine Tier (Backend)
- **Statutory Engine:** Deterministic rule evaluation in Python using relational and categorical operators (`GTE`, `LTE`, `EQUALS`, `IN`, `INTERSECT_ANY`, `RANGE`).
- **Convergence Engine:** Graph topology generator and pairwise evaluator enforcing explicit documentary citations.
- **Policy Change Impact Engine:** Detects downstream citizen impact when a gazette rule is amended, tagging affected saved action plans and logging administrative audit trails.

### 2.3 Persistence & Auditing Tier
- Dual-engine compatibility: SQLite for zero-configuration hackathon demos; PostgreSQL for clustered production deployment.
- Strict foreign key constraints with cascade behaviors (`ondelete="CASCADE"`, `ondelete="SET NULL"`).
- Immutable administrative audit logs for compliance review.
