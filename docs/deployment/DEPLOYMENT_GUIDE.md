# YojanaSaathi AI — Deployment & Operations Guide
**Document Version:** 3.0.0  
**Target Environments:** Local Development, Docker Containerization, Production Cloud (Render / Railway / AWS / VPS)

---

## 1. Quick Start (Local Development)

### 1.1 Prerequisites
- Python 3.11+ (tested on Python 3.13)
- Node.js 18+ & npm
- Git

### 1.2 Backend Startup
```bash
# Clone the repository
git clone https://github.com/arorautkarsh05-web/YojanaSaathi-AI.git
cd YojanaSaathi-AI

# Create virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Run migrations and seed verified scheme data
alembic -c backend/alembic.ini upgrade head
python -c "import sys; sys.path.insert(0, 'backend'); from app.db.session import SessionLocal; from app.services.scheme_seeder import seed_schemes_and_rules; db=SessionLocal(); seed_schemes_and_rules(db); db.close()"

# Start FastAPI server on port 8000
python -m uvicorn app.main:app --app-dir backend --reload --port 8000
```
Backend will be live at `http://127.0.0.1:8000` with Swagger docs at `http://127.0.0.1:8000/docs`.

### 1.3 Frontend Startup
```bash
# In a new terminal window:
cd frontend
npm install
npm run dev
```
Frontend will be live at `http://localhost:5173`.

---

## 2. Docker Containerized Deployment

To launch the complete application stack (PostgreSQL 16 + FastAPI Backend + Nginx/Vite Frontend) with a single command:

```bash
# Copy environment configuration
cp .env.example .env

# Generate secure secrets in .env:
# Windows PowerShell:
# (New-Guid).ToString("N")
# Linux:
# openssl rand -hex 32

# Build and start containers
docker-compose up -d --build

# Verify running containers and health checks
docker-compose ps
```

Health check probes:
- Backend live probe: `http://localhost:8000/live`
- Backend ready probe: `http://localhost:8000/ready`
- Comprehensive health probe: `http://localhost:8000/health`

---

## 3. Environment Variable Configuration

| Variable | Description | Default | Production Requirement |
|---|---|---|---|
| `SECRET_KEY` | HMAC signing key for JWT tokens | Development fallback | **MANDATORY: 64-char random hex** |
| `DATABASE_URL` | SQLAlchemy database connection URI | `sqlite:///./backend/yojanasaathi.db` | PostgreSQL connection string |
| `BACKEND_CORS_ORIGINS` | Allowed cross-origin domains | `["http://localhost:5173"]` | Set to production domain |
| `ENV` | Application environment flag | `development` | Set to `production` |
| `ADMIN_INITIAL_EMAIL` | Bootstrap admin account email | `admin@yojanasaathi.in` | Override in production |
| `ADMIN_INITIAL_PASSWORD` | Bootstrap admin password | `AdminSecurePass2026!` | **MANDATORY: Override in production** |

---

## 4. Production Hardening Checklist
- [x] Run behind HTTPS reverse proxy (Nginx, Traefik, or Cloudflare SSL termination).
- [x] Ensure `COOKIE_SECURE=true` and HTTPOnly flags on authentication cookies.
- [x] Verify database backups via scheduled `pg_dump` cron jobs.
- [x] Enforce rate limiting on authentication routes `/api/v1/auth/login`.
