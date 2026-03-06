"""
CUCEI MART - Stores Router
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select, func, col
from typing import List, Optional
from datetime import datetime
import aiofiles, os, uuid

from models.database import Store, Review, Product, User, get_session
from schemas.schemas import StoreCreate, StoreUpdate, StorePublic
from services.auth import get_current_user, require_entrepreneur

router = APIRouter(prefix="/stores", tags=["Tiendas"])

UPLOAD_DIR = "static/uploads"


def _enrich_store(store: Store, session: Session) -> dict:
    """Attach avg_rating and review_count to store dict."""
    reviews = session.exec(select(Review).where(Review.store_id == store.id)).all()
    avg     = round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else None
    d       = store.dict()
    d["avg_rating"]   = avg
    d["review_count"] = len(reviews)
    return d


# ─── Public ───────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[dict])
def list_stores(
    q        : Optional[str] = Query(None),
    category : Optional[str] = Query(None),
    featured : Optional[bool]= Query(None),
    session  : Session       = Depends(get_session),
):
    query = select(Store).where(Store.is_active == True)
    if q:
        query = query.where(Store.name.contains(q) | Store.description.contains(q))
    if category:
        query = query.where(Store.category == category)
    if featured is not None:
        query = query.where(Store.is_featured == featured)

    stores = session.exec(query.order_by(col(Store.total_sales).desc())).all()
    return [_enrich_store(s, session) for s in stores]


@router.get("/featured", response_model=List[dict])
def featured_stores(session: Session = Depends(get_session)):
    """Top 6 tiendas destacadas con calificacion."""
    stores = session.exec(
        select(Store)
        .where(Store.is_active == True)
        .order_by(col(Store.total_sales).desc())
        .limit(6)
    ).all()
    return [_enrich_store(s, session) for s in stores]


@router.get("/{store_id}", response_model=dict)
def get_store(store_id: int, session: Session = Depends(get_session)):
    store = session.get(Store, store_id)
    if not store or not store.is_active:
        raise HTTPException(404, "Tienda no encontrada")
    return _enrich_store(store, session)


# ─── Protected ────────────────────────────────────────────────────────────────

@router.post("/", response_model=StorePublic, status_code=201)
def create_store(
    data        : StoreCreate,
    session     : Session = Depends(get_session),
    current_user: User    = Depends(require_entrepreneur),
):
    if session.exec(select(Store).where(Store.owner_id == current_user.id)).first():
        raise HTTPException(400, "Ya tienes una tienda registrada")

    store = Store(
        owner_id      = current_user.id,
        name          = data.name,
        description   = data.description,
        category      = data.category,
        contact_email = data.contact_email,
        contact_phone = data.contact_phone,
        instagram_url = data.instagram_url,
    )
    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@router.patch("/my", response_model=StorePublic)
def update_my_store(
    data        : StoreUpdate,
    session     : Session = Depends(get_session),
    current_user: User    = Depends(require_entrepreneur),
):
    store = session.exec(select(Store).where(Store.owner_id == current_user.id)).first()
    if not store:
        raise HTTPException(404, "No tienes una tienda creada")

    if data.name          is not None: store.name          = data.name
    if data.description   is not None: store.description   = data.description
    if data.category      is not None: store.category      = data.category
    if data.contact_email is not None: store.contact_email = data.contact_email
    if data.contact_phone is not None: store.contact_phone = data.contact_phone
    if data.instagram_url is not None: store.instagram_url = data.instagram_url

    session.add(store)
    session.commit()
    session.refresh(store)
    return store


@router.post("/my/logo")
async def upload_logo(
    file        : UploadFile = File(...),
    session     : Session    = Depends(get_session),
    current_user: User       = Depends(require_entrepreneur),
):
    store = session.exec(select(Store).where(Store.owner_id == current_user.id)).first()
    if not store:
        raise HTTPException(404, "No tienes una tienda creada")

    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Solo se permiten imagenes")

    ext      = file.filename.split(".")[-1]
    filename = f"logo_{uuid.uuid4()}.{ext}"
    path     = os.path.join(UPLOAD_DIR, filename)
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())

    store.logo_url = f"/static/uploads/{filename}"
    session.add(store)
    session.commit()
    return {"logo_url": store.logo_url}
