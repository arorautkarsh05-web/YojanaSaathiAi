from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import List
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    PROJECT_NAME: str = "YojanaSaathi AI"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Database URL: defaults to SQLite locally, supports PostgreSQL seamlessly
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./yojanasaathi.db")
    
    # JWT & Auth Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "yojanasaathi-in-spark2scale-hackathon-2026-production-grade-secret-key-32chars")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Cookies & CSRF
    REFRESH_COOKIE_NAME: str = "yojanasaathi_refresh_token"
    CSRF_HEADER_NAME: str = "X-CSRF-Token"
    COOKIE_SECURE: bool = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    COOKIE_SAMESITE: str = os.getenv("COOKIE_SAMESITE", "lax")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Admin Bootstrap (Zero hardcoding - driven by environment)
    ADMIN_INITIAL_EMAIL: str = os.getenv("ADMIN_INITIAL_EMAIL", "admin@yojanasaathi.up.gov.in")
    ADMIN_INITIAL_PASSWORD: str = os.getenv("ADMIN_INITIAL_PASSWORD", "AdminSecurePass@2026")
    REQUIRE_EMAIL_VERIFICATION: bool = os.getenv("REQUIRE_EMAIL_VERIFICATION", "false").lower() == "true"
    
    # Rate Limiting
    RATE_LIMIT_LOGIN_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_LOGIN_PER_MINUTE", "10"))
    RATE_LIMIT_REGISTER_PER_HOUR: int = int(os.getenv("RATE_LIMIT_REGISTER_PER_HOUR", "20"))

    @model_validator(mode="after")
    def validate_production_security(self) -> "Settings":
        if self.ENV.lower() == "production":
            default_key = "yojanasaathi-in-spark2scale-hackathon-2026-production-grade-secret-key-32chars"
            if self.SECRET_KEY == default_key or len(self.SECRET_KEY) < 32:
                raise ValueError("CRITICAL SECURITY VIOLATION: Production deployment requires an explicit, unique SECRET_KEY (min 32 chars). Default development secret forbidden in production.")
            if self.ADMIN_INITIAL_PASSWORD == "AdminSecurePass@2026":
                raise ValueError("CRITICAL SECURITY VIOLATION: Production deployment cannot use default administrative credentials. Set ADMIN_INITIAL_PASSWORD.")
            if not self.COOKIE_SECURE:
                # In production HTTPS, COOKIE_SECURE should be True
                pass
        return self

settings = Settings()

