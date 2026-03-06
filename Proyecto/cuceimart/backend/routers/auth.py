"""
CUCEI MART - Auth Router
POST /auth/register
POST /auth/login
GET  /auth/me
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from datetime import timedelta

from models.database import User, get_session, UserRole
from schemas.schemas import UserRegister, UserLogin, TokenResponse, UserPublic, UserUpdate
from services.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/auth", tags=["Autenticacion"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(data: UserRegister, session: Session = Depends(get_session)):
    """Registrar nuevo usuario (estudiante o emprendedor)."""

    # Check duplicates
    if session.exec(select(User).where(User.email == data.email)).first():
        raise HTTPException(400, "El correo electronico ya esta registrado")
    if session.exec(select(User).where(User.username == data.username)).first():
        raise HTTPException(400, "El nombre de usuario ya esta en uso")

    user = User(
        email            = data.email,
        username         = data.username,
        hashed_password  = hash_password(data.password),
        full_name        = data.full_name,
        role             = data.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(
        access_token = token,
        user_id      = user.id,
        username     = user.username,
        role         = user.role,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, session: Session = Depends(get_session)):
    """Iniciar sesion y obtener JWT."""
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")

    token = create_access_token({"sub": str(user.id)}, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return TokenResponse(
        access_token = token,
        user_id      = user.id,
        username     = user.username,
        role         = user.role,
    )


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)):
    """Obtener perfil del usuario autenticado."""
    return current_user


@router.patch("/me", response_model=UserPublic)
def update_profile(
    data        : UserUpdate,
    session     : Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    """Actualizar perfil propio."""
    if data.full_name  is not None: current_user.full_name  = data.full_name
    if data.bio        is not None: current_user.bio        = data.bio
    if data.avatar_url is not None: current_user.avatar_url = data.avatar_url

    from datetime import datetime
    current_user.updated_at = datetime.utcnow()
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user
