"""
CUCEI MART - Products Router
Full CRUD + search/filter
"""

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlmodel import Session, select, func, col
from typing import Optional, List
from datetime import datetime
import aiofiles, os, uuid

from models.database import Product, Store, Category, User, get_session, ProductStatus
from schemas.schemas import ProductCreate, ProductUpdate, ProductPublic, PaginatedResponse
from services.auth import get_current_user, require_entrepreneur

router = APIRouter(prefix="/products", tags=["Productos"])

UPLOAD_DIR = "static/uploads"


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_store_of_user(session: Session, user: User) -> Store:
    store = session.exec(select(Store).where(Store.owner_id == user.id)).first()
    if not store:
        raise HTTPException(404, "Primero debes crear tu tienda")
    return store


# ─── Public endpoints ─────────────────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse)
def list_products(
    q          : Optional[str]   = Query(None, description="Busqueda por nombre o descripcion"),
    category   : Optional[str]   = Query(None),
    min_price  : Optional[float] = Query(None, ge=0),
    max_price  : Optional[float] = Query(None, ge=0),
    store_id   : Optional[int]   = Query(None),
    sort_by    : str             = Query("created_at", enum=["price", "total_sold", "views", "created_at", "name"]),
    order      : str             = Query("desc", enum=["asc", "desc"]),
    page       : int             = Query(1, ge=1),
    per_page   : int             = Query(20, ge=1, le=100),
    session    : Session         = Depends(get_session),
):
    """Listar y filtrar productos con paginacion."""
    query = select(Product).where(Product.status == ProductStatus.active)

    if q:
        query = query.where(
            Product.name.contains(q) | Product.description.contains(q) | Product.tags.contains(q)
        )
    if category:
        cat = session.exec(select(Category).where(Category.slug == category)).first()
        if cat:
            query = query.where(Product.category_id == cat.id)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if store_id:
        query = query.where(Product.store_id == store_id)

    sort_col = {
        "price"      : Product.price,
        "total_sold" : Product.total_sold,
        "views"      : Product.views,
        "created_at" : Product.created_at,
        "name"       : Product.name,
    }.get(sort_by, Product.created_at)

    if order == "asc":
        query = query.order_by(col(sort_col).asc())
    else:
        query = query.order_by(col(sort_col).desc())

    total   = session.exec(select(func.count()).select_from(query.subquery())).one()
    items   = session.exec(query.offset((page - 1) * per_page).limit(per_page)).all()

    return PaginatedResponse(
        items       = items,
        total       = total,
        page        = page,
        per_page    = per_page,
        total_pages = (total + per_page - 1) // per_page,
    )


@router.get("/featured", response_model=List[ProductPublic])
def featured_products(session: Session = Depends(get_session)):
    """Top 12 productos mas vendidos (estilo MercadoLibre)."""
    products = session.exec(
        select(Product)
        .where(Product.status == ProductStatus.active)
        .order_by(col(Product.total_sold).desc())
        .limit(12)
    ).all()
    return products


@router.get("/{product_id}", response_model=ProductPublic)
def get_product(product_id: int, session: Session = Depends(get_session)):
    product = session.get(Product, product_id)
    if not product or product.status == ProductStatus.inactive:
        raise HTTPException(404, "Producto no encontrado")
    # Increment views
    product.views += 1
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


# ─── Protected endpoints ──────────────────────────────────────────────────────

@router.post("/", response_model=ProductPublic, status_code=201)
def create_product(
    data        : ProductCreate,
    session     : Session = Depends(get_session),
    current_user: User    = Depends(require_entrepreneur),
):
    store   = _get_store_of_user(session, current_user)
    product = Product(
        store_id    = store.id,
        category_id = data.category_id,
        name        = data.name,
        description = data.description,
        price       = data.price,
        stock       = data.stock,
        tags        = data.tags,
    )
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.patch("/{product_id}", response_model=ProductPublic)
def update_product(
    product_id  : int,
    data        : ProductUpdate,
    session     : Session = Depends(get_session),
    current_user: User    = Depends(require_entrepreneur),
):
    store   = _get_store_of_user(session, current_user)
    product = session.get(Product, product_id)
    if not product or product.store_id != store.id:
        raise HTTPException(404, "Producto no encontrado o no tienes permiso")

    if data.name        is not None: product.name        = data.name
    if data.description is not None: product.description = data.description
    if data.price       is not None: product.price       = data.price
    if data.stock       is not None: product.stock       = data.stock
    if data.status      is not None: product.status      = data.status
    if data.tags        is not None: product.tags        = data.tags

    product.updated_at = datetime.utcnow()
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/{product_id}", status_code=204)
def delete_product(
    product_id  : int,
    session     : Session = Depends(get_session),
    current_user: User    = Depends(require_entrepreneur),
):
    store   = _get_store_of_user(session, current_user)
    product = session.get(Product, product_id)
    if not product or product.store_id != store.id:
        raise HTTPException(404, "Producto no encontrado o no tienes permiso")
    session.delete(product)
    session.commit()


@router.post("/{product_id}/image", response_model=ProductPublic)
async def upload_product_image(
    product_id  : int,
    file        : UploadFile = File(...),
    session     : Session    = Depends(get_session),
    current_user: User       = Depends(require_entrepreneur),
):
    store   = _get_store_of_user(session, current_user)
    product = session.get(Product, product_id)
    if not product or product.store_id != store.id:
        raise HTTPException(404, "Producto no encontrado")

    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Solo se permiten archivos de imagen")

    ext      = file.filename.split(".")[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    path     = os.path.join(UPLOAD_DIR, filename)

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    async with aiofiles.open(path, "wb") as f:
        await f.write(await file.read())

    product.image_url   = f"/static/uploads/{filename}"
    product.updated_at  = datetime.utcnow()
    session.add(product)
    session.commit()
    session.refresh(product)
    return product
