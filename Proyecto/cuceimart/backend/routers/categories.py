"""
CUCEI MART - Categories Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from models.database import Category, get_session
from schemas.schemas import CategoryCreate, CategoryPublic
from services.auth import require_admin

router = APIRouter(prefix="/categories", tags=["Categorias"])


@router.get("/", response_model=List[CategoryPublic])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


@router.post("/", response_model=CategoryPublic, status_code=201)
def create_category(
    data    : CategoryCreate,
    session : Session = Depends(get_session),
    _       : object  = Depends(require_admin),
):
    if session.exec(select(Category).where(Category.slug == data.slug)).first():
        raise HTTPException(400, "Ya existe una categoria con ese slug")

    cat = Category(**data.dict())
    session.add(cat)
    session.commit()
    session.refresh(cat)
    return cat


@router.delete("/{cat_id}", status_code=204)
def delete_category(
    cat_id  : int,
    session : Session = Depends(get_session),
    _       : object  = Depends(require_admin),
):
    cat = session.get(Category, cat_id)
    if not cat:
        raise HTTPException(404, "Categoria no encontrada")
    session.delete(cat)
    session.commit()
