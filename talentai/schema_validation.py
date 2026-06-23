"""Validate candidate records against candidate_schema.json.

Uses `jsonschema` when available (full draft-07 validation). Falls back to a
lightweight structural check so ingestion never hard-fails just because an
optional dependency is missing.
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from . import paths


@lru_cache(maxsize=1)
def load_schema() -> Dict:
    with open(paths.schema_file(), "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _validator():
    try:
        from jsonschema import Draft7Validator  # type: ignore

        return Draft7Validator(load_schema())
    except Exception:
        return None


_TOP_LEVEL_REQUIRED = (
    "candidate_id",
    "profile",
    "career_history",
    "education",
    "skills",
    "redrob_signals",
)


def validate_record(record: Dict) -> List[str]:
    """Return a list of validation error strings (empty == valid)."""
    v = _validator()
    if v is not None:
        return [f"{'/'.join(str(p) for p in e.path) or '<root>'}: {e.message}"
                for e in v.iter_errors(record)]

    # Lightweight fallback
    errors: List[str] = []
    for key in _TOP_LEVEL_REQUIRED:
        if key not in record:
            errors.append(f"<root>: missing required field '{key}'")
    cid = record.get("candidate_id", "")
    if not isinstance(cid, str) or not cid.startswith("CAND_") or len(cid) != 12:
        errors.append("candidate_id: must match CAND_XXXXXXX (7 digits)")
    if not isinstance(record.get("career_history", []), list):
        errors.append("career_history: must be an array")
    if not isinstance(record.get("skills", []), list):
        errors.append("skills: must be an array")
    return errors


def is_valid(record: Dict) -> bool:
    return not validate_record(record)


def validate_file(path: Optional[Path] = None, sample: Optional[int] = None) -> Tuple[int, int, List[str]]:
    """Validate a candidates file. Returns (valid_count, total, first_errors)."""
    from .data import iter_candidates

    total = 0
    valid = 0
    first_errors: List[str] = []
    for rec in iter_candidates(path):
        total += 1
        errs = validate_record(rec)
        if errs:
            if len(first_errors) < 20:
                first_errors.append(f"{rec.get('candidate_id', '?')}: {errs[0]}")
        else:
            valid += 1
        if sample is not None and total >= sample:
            break
    return valid, total, first_errors
