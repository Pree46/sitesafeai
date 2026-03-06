"""
SiteSafeAI — Dashboard Analytics Backend
Separate FastAPI service for the analytics dashboard.
Run: uvicorn backend.app:app --port 8001 --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.dashboard import router as dashboard_router
from backend.database import init_db

app = FastAPI(
    title="SiteSafeAI Dashboard API",
    description="Analytics backend for the SiteSafeAI safety monitoring dashboard",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard_router)

@app.get("/")
def root():
    return {
        "service": "SiteSafeAI Dashboard API",
        "version": "1.0.0",
        "docs": "/docs",
    }
