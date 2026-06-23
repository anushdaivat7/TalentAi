"""In-memory data store backing the API.

Loads the explainable ranking (results/ranked_candidates.json) and the structured
job profile, and exposes derived analytics for the dashboard, search and chatbot.
Also provides optional MongoDB access for raw candidate lookups.
"""
from __future__ import annotations

import json
import sys
import threading
from pathlib import Path
from typing import Dict, List, Optional

from .config import ROOT, settings

# Make the talentai package importable for on-the-fly ranking of samples.
sys.path.insert(0, str(ROOT))


class Store:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.ranked: List[Dict] = []
        self.by_id: Dict[str, Dict] = {}
        self.job_profile: Dict = {}
        self.trap_stats: Dict = {}
        self.load()

    # ------------------------------------------------------------------ #
    def load(self) -> None:
        with self._lock:
            self.ranked = self._load_json(settings.RANKED_JSON, default=[])
            self.by_id = {r["candidate_id"]: r for r in self.ranked}
            self.job_profile = self._load_json(settings.JOB_PROFILE_JSON, default={})
            self.trap_stats = self._load_json(settings.TRAP_STATS_JSON, default={})

    @staticmethod
    def _load_json(path: Path, default):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return default

    @property
    def loaded(self) -> bool:
        return bool(self.ranked)

    # ------------------------------------------------------------------ #
    def mongo_collection(self):
        if not settings.MONGODB_URI:
            return None
        try:
            from pymongo import MongoClient

            client = MongoClient(settings.MONGODB_URI, serverSelectionTimeoutMS=5000)
            return client[settings.MONGODB_DB][settings.MONGODB_COLLECTION]
        except Exception:
            return None

    def raw_candidate(self, candidate_id: str) -> Optional[Dict]:
        col = self.mongo_collection()
        if col is not None:
            doc = col.find_one({"candidate_id": candidate_id}, {"_id": 0})
            if doc:
                return doc
        return None


store = Store()
