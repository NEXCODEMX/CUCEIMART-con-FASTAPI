"""
CUCEI MART - Pydantic Schemas (pydantic v1 compatible)
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Any
from datetime import datetime


# ─── Auth ─────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    email     : EmailStr
    username  : str       = Field(min_length=3, max_length=80)
    password  : str       = Field(min_length=8, max_length=128)
    full_name : str       = Field(min_length=2, max_length=200)
    role      : str       = "student"

    @validator("username")
    def username_alphanumeric(cls, v):
        import re
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Solo letras, numeros y guion bajo")
        return v

    @validator("role")
    def role_valid(cls, v):
        if v not in ("student", "entrepreneur", "admin"):
            raise ValueError("Rol invalido")
        return v

    class Config:
        schema_extra = {
            "example": {
                "email": "juan@alumnos.udg.mx",
                "username": "juan_udg",
                "password": "SecurePass123",
                "full_name": "Juan Carlos Perez",
                "role": "student"
            }
        }


class UserLogin(BaseModel):
    email    : EmailStr
    password : str


class TokenResponse(BaseModel):
    access_token : str
    token_type   : str = "bearer"
    user_id      : int
    username     : str
    role         : str


# ─── User ─────────────────────────────────────────────────────────────────────

class UserPublic(BaseModel):
    id         : int
    username   : str
    full_name  : str
    role       : str
    avatar_url : Optional[str]
    bio        : Optional[str]
    is_verified: bool
    created_at : Optional[datetime]

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    full_name  : Optional[str]
    bio        : Optional[str]
    avatar_url : Optional[str]


# ─── Store ────────────────────────────────────────────────────────────────────

class StoreCreate(BaseModel):
    name          : str  = Field(min_length=2, max_length=200)
    description   : str  = Field(min_length=10, max_length=1000)
    category      : str
    contact_email : Optional[str] = None
    contact_phone : Optional[str] = None
    instagram_url : Optional[str] = None


class StoreUpdate(BaseModel):
    name          : Optional[str] = None
    description   : Optional[str] = None
    category      : Optional[str] = None
    contact_email : Optional[str] = None
    contact_phone : Optional[str] = None
    instagram_url : Optional[str] = None


class StorePublic(BaseModel):
    id            : int
    name          : str
    description   : str
    category      : str
    logo_url      : Optional[str]
    banner_url    : Optional[str]
    contact_email : Optional[str]
    contact_phone : Optional[str]
    instagram_url : Optional[str]
    total_sales   : int
    is_featured   : bool
    avg_rating    : Optional[float] = None
    review_count  : Optional[int]   = None
    created_at    : Optional[datetime]

    class Config:
        orm_mode = True


# ─── Category ─────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name        : str
    slug        : str
    description : Optional[str] = None
    icon        : Optional[str] = None
    color       : Optional[str] = None

    @validator("slug")
    def slug_format(cls, v):
        import re
        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError("Slug solo puede tener minusculas, numeros y guiones")
        return v


class CategoryPublic(BaseModel):
    id          : int
    name        : str
    slug        : str
    description : Optional[str]
    icon        : Optional[str]
    color       : Optional[str]

    class Config:
        orm_mode = True


# ─── Product ──────────────────────────────────────────────────────────────────

class ProductCreate(BaseModel):
    name        : str   = Field(min_length=2, max_length=200)
    description : str   = Field(min_length=10, max_length=2000)
    price       : float = Field(gt=0)
    stock       : int   = Field(ge=0)
    category_id : Optional[int] = None
    tags        : Optional[str] = None


class ProductUpdate(BaseModel):
    name        : Optional[str]   = None
    description : Optional[str]   = None
    price       : Optional[float] = Field(default=None, gt=0)
    stock       : Optional[int]   = Field(default=None, ge=0)
    status      : Optional[str]   = None
    tags        : Optional[str]   = None


class ProductPublic(BaseModel):
    id          : int
    store_id    : int
    name        : str
    description : str
    price       : float
    stock       : int
    image_url   : Optional[str]
    status      : str
    tags        : Optional[str]
    total_sold  : int
    views       : int
    created_at  : Optional[datetime]

    class Config:
        orm_mode = True


# ─── Review ───────────────────────────────────────────────────────────────────

class ReviewCreate(BaseModel):
    store_id : int
    rating   : int   = Field(ge=1, le=5)
    title    : Optional[str] = None
    comment  : str   = Field(min_length=5, max_length=1000)


class ReviewPublic(BaseModel):
    id                   : int
    store_id             : int
    rating               : int
    title                : Optional[str]
    comment              : str
    is_verified_purchase : bool
    reviewer             : UserPublic
    created_at           : Optional[datetime]

    class Config:
        orm_mode = True


# ─── Cart ─────────────────────────────────────────────────────────────────────

class CartItemCreate(BaseModel):
    product_id : int
    quantity   : int = Field(default=1, ge=1)


# ─── Pagination ───────────────────────────────────────────────────────────────

class PaginatedResponse(BaseModel):
    items       : List[Any]
    total       : int
    page        : int
    per_page    : int
    total_pages : int
