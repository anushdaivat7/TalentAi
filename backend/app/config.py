"""Backend configuration (env-driven, sane local defaults)."""
from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class Settings:
    APP_NAME = "TalentAI API"
    VERSION = "1.0.0"

    # CORS - the Vite dev server origin(s)
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:4173",
    ).split(",")

    # Mongo (optional)
    MONGODB_URI = os.getenv("MONGODB_URI", "")
    MONGODB_DB = os.getenv("MONGODB_DB", "talentai")
    MONGODB_COLLECTION = os.getenv("MONGODB_COLLECTION", "candidates")

    # Artifacts produced by the pipeline
    RANKED_JSON = ROOT / "results" / "ranked_candidates.json"
    JOB_PROFILE_JSON = ROOT / "artifacts" / "job_profile.json"
    TRAP_STATS_JSON = ROOT / "results" / "trap_stats.json"

    # Gemini (optional)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


settings = Settings()
