from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router
from app.core.config import settings
from app.db.session import init_db

# Create FastAPI app
app = FastAPI(title=settings.APP_NAME)

# Enable CORS so Swagger UI + frontend can keep you logged in
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Swagger UI / frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DB on startup
@app.on_event("startup")
def on_startup():
    init_db()

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

# Include API routes (auth, users, etc.)
app.include_router(api_router)

# app/app/main.py
from __future__ import annotations
from fastapi import FastAPI
from app.app.routers.ai import router as ai_router

app = FastAPI(title="Aurexus")
app.include_router(ai_router)

# optional health
@app.get("/health")
def health():
    return {"ok": True}


