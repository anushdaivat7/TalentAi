"""Filesystem path resolution for the project and the challenge data bundle."""
from __future__ import annotations

import os
from pathlib import Path

# Repo root = parent of the `talentai` package directory.
ROOT = Path(__file__).resolve().parent.parent

# The official challenge bundle (kept outside source control). The folder name
# contains brackets/spaces, so we resolve it dynamically and allow overrides.
DEFAULT_BUNDLE = ROOT / "[PUB] India_runs_data_and_ai_challenge" / "India_runs_data_and_ai_challenge"

# Artifacts produced by the pipeline.
ARTIFACTS = ROOT / "artifacts"
RESULTS = ROOT / "results"

ARTIFACTS.mkdir(exist_ok=True)
RESULTS.mkdir(exist_ok=True)


def bundle_dir() -> Path:
    """Return the challenge bundle directory (overridable via TALENTAI_BUNDLE)."""
    env = os.getenv("TALENTAI_BUNDLE")
    if env:
        return Path(env)
    return DEFAULT_BUNDLE


def candidates_file() -> Path:
    """Locate the candidate pool file (prefers .jsonl, falls back to .jsonl.gz)."""
    env = os.getenv("TALENTAI_CANDIDATES")
    if env:
        return Path(env)
    b = bundle_dir()
    for name in ("candidates.jsonl", "candidates.jsonl.gz"):
        p = b / name
        if p.exists():
            return p
    return b / "candidates.jsonl"


def schema_file() -> Path:
    return bundle_dir() / "candidate_schema.json"


def sample_candidates_file() -> Path:
    return bundle_dir() / "sample_candidates.json"


# Standard artifact locations
EMBEDDINGS_NPY = ARTIFACTS / "candidate_embeddings.npy"
EMBEDDINGS_IDS = ARTIFACTS / "candidate_ids.json"
FAISS_INDEX = ARTIFACTS / "candidates.faiss"
JOB_EMBEDDING_NPY = ARTIFACTS / "job_embedding.npy"
JOB_PROFILE_JSON = ARTIFACTS / "job_profile.json"

# Ranking outputs consumed by the dashboard/backend
RANKED_JSON = RESULTS / "ranked_candidates.json"
SUBMISSION_CSV = RESULTS / "submission.csv"
TRAP_STATS_JSON = RESULTS / "trap_stats.json"
