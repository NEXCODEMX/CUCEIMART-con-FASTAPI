"""
CUCEI MART - Main FastAPI Application
Run: uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from models.database import create_db_and_tables
from routers import auth, products, stores, reviews, categories, stats

# ─── App init ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title       = "CUCEI MART API",
    description = "Plataforma de e-commerce universitario del CUCEI — Nexcode",
    version     = "1.0.0",
    docs_url    = "/docs",
    redoc_url   = "/redoc",
)

# ─── CORS ─────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins  = ["*"],   # In production: ["https://cuceimart.udg.mx"]
    allow_methods  = ["*"],
    allow_headers  = ["*"],
)

# ─── Static files ─────────────────────────────────────────────────────────────

os.makedirs("static/uploads", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve frontend
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(FRONTEND_DIR):
    app.mount("/app", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

# ─── Routers ──────────────────────────────────────────────────────────────────

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(stores.router)
app.include_router(reviews.router)
app.include_router(categories.router)
app.include_router(stats.router)

# ─── Startup ──────────────────────────────────────────────────────────────────

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print("CUCEI MART API iniciada correctamente.")


@app.get("/", tags=["Root"])
def root():
    return {
        "app"     : "CUCEI MART",
        "version" : "1.0.0",
        "docs"    : "/docs",
        "status"  : "running",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
