"""
CUCEI MART - Stats & Search Router
"""

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select, func, col
from typing import Optional

from models.database import (
    User, Store, Product, Order, Review, Category,
    get_session, UserRole, ProductStatus
)

router = APIRouter(prefix="/stats", tags=["Estadisticas"])


@router.get("/platform")
def platform_stats(session: Session = Depends(get_session)):
    """Estadisticas generales de la plataforma."""
    total_users         = session.exec(select(func.count(User.id))).one()
    total_entrepreneurs = session.exec(
        select(func.count(User.id)).where(User.role == UserRole.entrepreneur)
    ).one()
    total_stores   = session.exec(select(func.count(Store.id)).where(Store.is_active == True)).one()
    total_products = session.exec(select(func.count(Product.id)).where(Product.status == ProductStatus.active)).one()
    total_orders   = session.exec(select(func.count(Order.id))).one()

    # Featured stores - top by sales with avg rating
    top_stores = session.exec(
        select(Store)
        .where(Store.is_active == True)
        .order_by(col(Store.total_sales).desc())
        .limit(6)
    ).all()

    featured = []
    for s in top_stores:
        reviews   = session.exec(select(Review).where(Review.store_id == s.id)).all()
        avg       = round(sum(r.rating for r in reviews) / len(reviews), 2) if reviews else 0
        d         = s.dict()
        d["avg_rating"]   = avg
        d["review_count"] = len(reviews)
        featured.append(d)

    # Top products
    top_products = session.exec(
        select(Product)
        .where(Product.status == ProductStatus.active)
        .order_by(col(Product.total_sold).desc())
        .limit(8)
    ).all()

    return {
        "total_users"         : total_users,
        "total_entrepreneurs" : total_entrepreneurs,
        "total_stores"        : total_stores,
        "total_products"      : total_products,
        "total_orders"        : total_orders,
        "featured_stores"     : featured,
        "top_products"        : top_products,
    }


@router.get("/search")
def global_search(
    q       : str     = Query(..., min_length=1),
    session : Session = Depends(get_session),
):
    """Busqueda global en productos y tiendas."""
    products = session.exec(
        select(Product)
        .where(
            Product.status == ProductStatus.active,
            (Product.name.contains(q) | Product.description.contains(q) | Product.tags.contains(q))
        )
        .limit(10)
    ).all()

    stores = session.exec(
        select(Store)
        .where(
            Store.is_active == True,
            (Store.name.contains(q) | Store.description.contains(q) | Store.category.contains(q))
        )
        .limit(6)
    ).all()

    return {
        "products" : products,
        "stores"   : stores,
        "total"    : len(products) + len(stores),
    }
