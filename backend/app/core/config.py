import os
import json
import secrets
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator, field_validator

def get_cors_origins() -> List[str]:
    raw = os.getenv("BACKEND_CORS_ORIGINS", "")
    default_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    if not raw:
        return default_origins
    if raw.strip() == "*":
        return ["*"]
    custom = [origin.strip() for origin in raw.split(",") if origin.strip()]
    return list(dict.fromkeys(default_origins + custom))

def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///./yojanasaathi.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    PROJECT_NAME: str = "YojanaSaathi AI"
    VERSION: str = "3.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENV: str = os.getenv("ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # Database URL: defaults to SQLite locally, supports PostgreSQL seamlessly
    DATABASE_URL: str = get_database_url()
    
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
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = get_cors_origins()

    @field_validator("BACKEND_CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str or v_str == "*":
                return ["*"]
            if v_str.startswith("[") and v_str.endswith("]"):
                try:
                    parsed = json.loads(v_str)
                    if isinstance(parsed, list):
                        return parsed
                except Exception:
                    pass
            return [origin.strip() for origin in v_str.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return ["*"]
    
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
            if not self.SECRET_KEY or self.SECRET_KEY == default_key or len(self.SECRET_KEY) < 32:
                # In production, if SECRET_KEY is not explicitly set, auto-generate a secure random 64-char key
                self.SECRET_KEY = secrets.token_hex(32)
            if self.ADMIN_INITIAL_PASSWORD == "AdminSecurePass@2026":
                # In production, if ADMIN_INITIAL_PASSWORD is default, auto-generate a secure password
                self.ADMIN_INITIAL_PASSWORD = secrets.token_urlsafe(16) + "@2026"
            if not self.COOKIE_SECURE:
                self.COOKIE_SECURE = True
            if self.COOKIE_SAMESITE == "lax":
                # Cross-site cookie for decoupled frontend/backend on Render
                self.COOKIE_SAMESITE = "none"
        if self.DATABASE_URL.startswith("postgres://"):
            self.DATABASE_URL = self.DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return self

settings = Settings()

