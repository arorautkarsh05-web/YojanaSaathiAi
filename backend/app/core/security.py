import secrets
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError
from app.core.config import settings

# Argon2id password hasher with recommended RFC 9106 memory and time parameters
ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4, hash_len=32)

def hash_password(password: str) -> str:
    """Hashes password using Argon2id."""
    return ph.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against an Argon2id hash."""
    try:
        return ph.verify(hashed_password, plain_password)
    except (VerifyMismatchError, InvalidHashError):
        return False

def hash_token(raw_token: str) -> str:
    """Computes a SHA-256 hash of opaque tokens before storing in database."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

def generate_opaque_token() -> str:
    """Generates a cryptographically secure random string."""
    return secrets.token_urlsafe(32)

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Creates a short-lived signed JWT access token."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": now,
        "iss": "yojanasaathi-auth",
        "aud": "yojanasaathi-api"
    })
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """Decodes and validates JWT token with explicit algorithm allow-list."""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer="yojanasaathi-auth",
            audience="yojanasaathi-api"
        )
        return payload
    except jwt.PyJWTError:
        return None

