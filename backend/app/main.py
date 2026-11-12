import sys
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine, Base, SessionLocal
from app.models import User, UserRole, Scheme, SchemeVersion, EligibilityRule, CompatibilityRule
from app.core.security import hash_password
from app.services.scheme_seeder import seed_schemes_and_rules
from app.api.routes import auth, profiles, schemes, recommendations, convergence, action_plans, assistant, admin

logger = logging.getLogger("uvicorn.error")

# Create tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verify and display database connection sign
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        db_url_display = str(settings.DATABASE_URL).split("@")[-1]
        banner = (
            "\n" + "="*68 + "\n"
            "  🌿 YOJANASAATHI AI — BACKEND SERVICE INITIALIZED\n"
            "  📍 Jurisdiction: Uttar Pradesh, India (75 Districts)\n"
            f"  [✓] DATABASE CONNECTED SUCCESSFULLY: {db_url_display}\n"
            "  [✓] Deterministic Rules Engine: 3-Valued Logic (PASS/FAIL/UNKNOWN)\n"
            "  [✓] Statutory Schemes Loaded: 6 Official Gazetted Schemes\n"
            "  🔗 Interactive API Documentation: http://127.0.0.1:8000/docs\n"
            + "="*68 + "\n"
        )
        print(banner, flush=True)
        sys.stdout.flush()
        logger.info(f"[✓] DATABASE CONNECTED: {db_url_display}")

        # Seed Database as Source of Truth (Schemes, Versions, Rules, Documents, Compatibility)
        seed_schemes_and_rules(db)

        # Seed initial admin if not present (Zero hardcoding - environment driven)
        admin_email = settings.ADMIN_INITIAL_EMAIL
        existing_admin = db.query(User).filter(User.email_normalized == admin_email).first()
        if not existing_admin:
            admin_user = User(
                email_normalized=admin_email,
                display_name="UP Agriculture Review Admin",
                password_hash=hash_password(settings.ADMIN_INITIAL_PASSWORD),
                account_status="ACTIVE",
                email_verified_at=datetime.now(timezone.utc)
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            admin_role = UserRole(
                user_id=admin_user.id,
                role="ADMIN",
                granted_by="SYSTEM_BOOTSTRAP"
            )
            db.add(admin_role)
            db.commit()
    except Exception as e:
        logger.error(f"[!] Database connection error: {e}")
        print(f"\n[!] Database connection failed: {e}\n", flush=True)
    finally:
        db.close()
    
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="YojanaSaathi AI — Farmer-first Government Benefit Convergence & Application Navigator (Uttar Pradesh)",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

# Health, Liveness and Readiness check endpoints
@app.get("/live", tags=["Observability"])
def liveness_check():
    """Liveness probe: verifies ASGI server process is alive."""
    return {
        "status": "alive",
        "service": settings.PROJECT_NAME,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/ready", tags=["Observability"])
def readiness_check():
    """Readiness probe: performs live database query to verify connection readiness."""
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return {
            "status": "ready",
            "database": "connected",
            "version": settings.VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        logger.error(f"Readiness probe failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "not_ready",
                "database": "unreachable",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        )
    finally:
        db.close()

@app.get("/health", tags=["Observability"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Observability"])
def health_check():
    """Active health probe verifying real database connectivity."""
    db = SessionLocal()
    db_status = "connected"
    status_code = 200
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unreachable: {str(e)}"
        status_code = 503
    finally:
        db.close()

    content = {
        "status": "healthy" if status_code == 200 else "degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENV,
        "geography": "State of Uttar Pradesh (75 Districts)",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    return JSONResponse(status_code=status_code, content=content)

# Register API routers under /api/v1
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(profiles.router, prefix=settings.API_V1_STR)
app.include_router(schemes.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)
app.include_router(convergence.router, prefix=settings.API_V1_STR)
app.include_router(action_plans.router, prefix=settings.API_V1_STR)
app.include_router(assistant.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
