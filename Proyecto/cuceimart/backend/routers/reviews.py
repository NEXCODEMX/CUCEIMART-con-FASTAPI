"""
CUCEI MART - Reviews Router
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional

from models.database import Review, Store, User, get_session
from schemas.schemas import ReviewCreate, ReviewPublic
from services.auth import get_current_user

router = APIRouter(prefix="/reviews", tags=["Resenas"])


@router.get("/store/{store_id}", response_model=List[ReviewPublic])
def get_store_reviews(
    store_id : int,
    page     : int = Query(1, ge=1),
    per_page : int = Query(10, ge=1, le=50),
    session  : Session = Depends(get_session),
):
    store = session.get(Store, store_id)
    if not store:
        raise HTTPException(404, "Tienda no encontrada")

    reviews = session.exec(
        select(Review)
        .where(Review.store_id == store_id)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    ).all()
    return reviews


@router.post("/", response_model=ReviewPublic, status_code=201)
def create_review(
    data        : ReviewCreate,
    session     : Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    store = session.get(Store, data.store_id)
    if not store:
        raise HTTPException(404, "Tienda no encontrada")
    if store.owner_id == current_user.id:
        raise HTTPException(400, "No puedes resenir tu propia tienda")

    # One review per user per store
    existing = session.exec(
        select(Review).where(
            Review.store_id == data.store_id,
            Review.reviewer_id == current_user.id
        )
    ).first()
    if existing:
        raise HTTPException(400, "Ya dejaste una resena para esta tienda")

    review = Review(
        store_id    = data.store_id,
        reviewer_id = current_user.id,
        rating      = data.rating,
        title       = data.title,
        comment     = data.comment,
    )
    session.add(review)
    session.commit()
    session.refresh(review)
    return review


@router.delete("/{review_id}", status_code=204)
def delete_review(
    review_id   : int,
    session     : Session = Depends(get_session),
    current_user: User    = Depends(get_current_user),
):
    review = session.get(Review, review_id)
    if not review:
        raise HTTPException(404, "Resena no encontrada")
    if review.reviewer_id != current_user.id:
        raise HTTPException(403, "No tienes permiso para eliminar esta resena")
    session.delete(review)
    session.commit()
