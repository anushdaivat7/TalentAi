"""TalentAI FastAPI application entrypoint.

Serves the recruiter dashboard, search, explainability, chatbot and submission
APIs over the ranked-candidate artifacts produced by the ranking pipeline.

Run:
    uvicorn app.main:app --reload --port 8000   (from the backend/ directory)
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .routers import candidates, chat, dashboard, submission
from .store import store

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router)
app.include_router(candidates.router)
app.include_router(chat.router)
app.include_router(submission.router)


@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "ranking_loaded": store.loaded,
        "ranked_count": len(store.ranked),
        "job_profile_loaded": bool(store.job_profile),
    }


@app.post("/api/reload")
def reload_data():
    store.load()
    return {"reloaded": True, "ranked_count": len(store.ranked)}


@app.get("/")
def root():
    return {"app": settings.APP_NAME, "version": settings.VERSION, "docs": "/docs"}
