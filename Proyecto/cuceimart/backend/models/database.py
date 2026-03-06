"""
CUCEI MART - Database Models
SQLModel + SQLite  |  Compatible: sqlmodel==0.0.16 + pydantic==1.x
"""

from sqlmodel import SQLModel, Field, Relationship, create_engine, Session
from typing import Optional, List
from datetime import datetime
from enum import Enum
import os

DATABASE_URL = "sqlite:///./cuceimart.db"
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})


# ─── Enums ────────────────────────────────────────────────────────────────────

class UserRole(str, Enum):
    student      = "student"
    entrepreneur = "entrepreneur"
    admin        = "admin"


class ProductStatus(str, Enum):
    active   = "active"
    inactive = "inactive"
    sold_out = "sold_out"


class OrderStatus(str, Enum):
    pending   = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"


# ─── User ─────────────────────────────────────────────────────────────────────

class User(SQLModel, table=True):
    __tablename__ = "users"

    id             : Optional[int] = Field(default=None, primary_key=True)
    email          : str           = Field(unique=True, index=True)
    username       : str           = Field(unique=True, index=True)
    hashed_password: str
    full_name      : str
    role           : str           = Field(default="student")
    avatar_url     : Optional[str] = Field(default=None)
    bio            : Optional[str] = Field(default=None)
    is_active      : bool          = Field(default=True)
    is_verified    : bool          = Field(default=False)
    created_at     : Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at     : Optional[datetime] = Field(default_factory=datetime.utcnow)

    store          : Optional["Store"]    = Relationship(back_populates="owner")
    reviews_given  : List["Review"]       = Relationship(back_populates="reviewer")
    cart_items     : List["CartItem"]     = Relationship(back_populates="user")
    orders         : List["Order"]        = Relationship(back_populates="buyer")


# ─── Store ────────────────────────────────────────────────────────────────────

class Store(SQLModel, table=True):
    __tablename__ = "stores"

    id            : Optional[int] = Field(default=None, primary_key=True)
    owner_id      : int           = Field(foreign_key="users.id", unique=True)
    name          : str
    description   : str
    category      : str
    logo_url      : Optional[str] = Field(default=None)
    banner_url    : Optional[str] = Field(default=None)
    contact_email : Optional[str] = Field(default=None)
    contact_phone : Optional[str] = Field(default=None)
    instagram_url : Optional[str] = Field(default=None)
    total_sales   : int           = Field(default=0)
    is_featured   : bool          = Field(default=False)
    is_active     : bool          = Field(default=True)
    created_at    : Optional[datetime] = Field(default_factory=datetime.utcnow)

    owner    : Optional[User]    = Relationship(back_populates="store")
    products : List["Product"]   = Relationship(back_populates="store")
    reviews  : List["Review"]    = Relationship(back_populates="store")


# ─── Category ─────────────────────────────────────────────────────────────────

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id          : Optional[int] = Field(default=None, primary_key=True)
    name        : str           = Field(unique=True)
    slug        : str           = Field(unique=True, index=True)
    description : Optional[str] = Field(default=None)
    icon        : Optional[str] = Field(default=None)
    color       : Optional[str] = Field(default=None)

    products    : List["Product"] = Relationship(back_populates="category")


# ─── Product ──────────────────────────────────────────────────────────────────

class Product(SQLModel, table=True):
    __tablename__ = "products"

    id          : Optional[int] = Field(default=None, primary_key=True)
    store_id    : int           = Field(foreign_key="stores.id", index=True)
    category_id : Optional[int] = Field(default=None, foreign_key="categories.id")
    name        : str
    description : str
    price       : float
    stock       : int           = Field(default=0)
    image_url   : Optional[str] = Field(default=None)
    status      : str           = Field(default="active")
    tags        : Optional[str] = Field(default=None)
    total_sold  : int           = Field(default=0)
    views       : int           = Field(default=0)
    created_at  : Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at  : Optional[datetime] = Field(default_factory=datetime.utcnow)

    store       : Optional[Store]     = Relationship(back_populates="products")
    category    : Optional[Category]  = Relationship(back_populates="products")
    cart_items  : List["CartItem"]    = Relationship(back_populates="product")
    order_items : List["OrderItem"]   = Relationship(back_populates="product")


# ─── Review ───────────────────────────────────────────────────────────────────

class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id                   : Optional[int] = Field(default=None, primary_key=True)
    store_id             : int           = Field(foreign_key="stores.id", index=True)
    reviewer_id          : int           = Field(foreign_key="users.id")
    rating               : int
    title                : Optional[str] = Field(default=None)
    comment              : str
    is_verified_purchase : bool          = Field(default=False)
    created_at           : Optional[datetime] = Field(default_factory=datetime.utcnow)

    store    : Optional[Store] = Relationship(back_populates="reviews")
    reviewer : Optional[User]  = Relationship(back_populates="reviews_given")


# ─── Cart ─────────────────────────────────────────────────────────────────────

class CartItem(SQLModel, table=True):
    __tablename__ = "cart_items"

    id         : Optional[int] = Field(default=None, primary_key=True)
    user_id    : int           = Field(foreign_key="users.id")
    product_id : int           = Field(foreign_key="products.id")
    quantity   : int           = Field(default=1)
    added_at   : Optional[datetime] = Field(default_factory=datetime.utcnow)

    user    : Optional[User]    = Relationship(back_populates="cart_items")
    product : Optional[Product] = Relationship(back_populates="cart_items")


# ─── Order ────────────────────────────────────────────────────────────────────

class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id           : Optional[int] = Field(default=None, primary_key=True)
    buyer_id     : int           = Field(foreign_key="users.id")
    status       : str           = Field(default="pending")
    total_amount : float         = Field(default=0.0)
    notes        : Optional[str] = Field(default=None)
    created_at   : Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at   : Optional[datetime] = Field(default_factory=datetime.utcnow)

    buyer : Optional[User]     = Relationship(back_populates="orders")
    items : List["OrderItem"]  = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id         : Optional[int] = Field(default=None, primary_key=True)
    order_id   : int           = Field(foreign_key="orders.id")
    product_id : int           = Field(foreign_key="products.id")
    quantity   : int
    unit_price : float

    order   : Optional[Order]   = Relationship(back_populates="items")
    product : Optional[Product] = Relationship(back_populates="order_items")


# ─── DB helpers ───────────────────────────────────────────────────────────────

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
