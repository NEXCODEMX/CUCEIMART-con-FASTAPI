"""
CUCEI MART - Authentication Service
JWT tokens + bcrypt password hashing (bcrypt direct, no passlib)
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from models.database import User, get_session
import os

# ─── Config ───────────────────────────────────────────────────────────────────

SECRET_KEY    = os.getenv("SECRET_KEY", "cuceimart-super-secret-key-change-in-production-2025")
ALGORITHM     = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

bearer_scheme = HTTPBearer()


# ─── Password helpers ─────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    """Hash a plain-text password with bcrypt."""
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ─── JWT helpers ──────────────────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire    = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


# ─── Dependencies ─────────────────────────────────────────────────────────────

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    session: Session = Depends(get_session),
) -> User:
    payload = decode_token(credentials.credentials)
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Token invalido")

    user = session.get(User, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")
    return user


def require_entrepreneur(current_user: User = Depends(get_current_user)) -> User:
    from models.database import UserRole
    if current_user.role not in (UserRole.entrepreneur, UserRole.admin):
        raise HTTPException(status_code=403, detail="Se requiere cuenta de emprendedor")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    from models.database import UserRole
    if current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Se requieren privilegios de administrador")
    return current_user
