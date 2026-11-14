# Contributing to YojanaSaathi AI

Thank you for your interest in contributing to **YojanaSaathi AI (योजना साथी AI)**. We welcome community and policy contributions that improve agricultural accessibility, evidence accuracy, and software reliability for farmers.

---

## 1. Core Principles for Contributors

1. **Evidence Grounding is Mandatory:** Never contribute a scheme rule, deadline, or benefit without an authoritative government source (Gazette of India, Ministry Circular, State Government Order).
2. **Three-Valued Logic:** All eligibility criteria must account for missing data (`UNKNOWN`) rather than assuming `PASS`.
3. **No Flawed Transitivity:** Multi-scheme compatibility must be proven pairwise with documentary citations.
4. **Accessible First:** Ensure all user interfaces adhere to WCAG 2.2 AA accessibility guidelines and support Hindi and multilingual terminology.

---

## 2. Local Development Setup

### 2.1 Backend Setup
```bash
# Navigate to backend
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations and seed verified schemes
alembic upgrade head
python -c "from app.db.session import SessionLocal; from app.services.scheme_seeder import seed_schemes_and_rules; db = SessionLocal(); seed_schemes_and_rules(db); db.close()"

# Start development server
uvicorn app.main:app --reload --port 8000
```

### 2.2 Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

---

## 3. Running Automated Tests

Before submitting a Pull Request, verify that all test suites pass:

```bash
# Run backend test suite (unit, integration, postgresql compatibility)
pytest backend/tests

# Verify frontend TypeScript types and production build
npm --prefix frontend run build
```

---

## 4. Submitting a Pull Request
- Create a feature branch (`git checkout -b feature/verified-scheme-enhancement`).
- Commit changes with descriptive messages (`git commit -m "feat(policy): update PMKSY-PDMC subsidy guideline citations"`).
- Push to your fork and submit a PR to `main`.
