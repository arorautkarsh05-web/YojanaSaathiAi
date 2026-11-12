from typing import Optional
from fastapi import Depends, HTTPException, status, Header, Request
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import decode_access_token
from app.models import User

def get_token_from_header(authorization: Optional[str] = Header(None)) -> Optional[str]:
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ")[1]
    return None

def get_current_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_header)
) -> User:
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or tampered token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if user.account_status != "ACTIVE":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is not active.")
    return user

def get_optional_user(
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(get_token_from_header)
) -> Optional[User]:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    user_id = payload["sub"]
    return db.query(User).filter(User.id == user_id, User.account_status == "ACTIVE").first()

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    roles = [r.role for r in current_user.roles]
    if "ADMIN" not in roles and "SUPER_ADMIN" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrative privileges required."
        )
    return current_user

