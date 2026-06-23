"""Phase 9 - write a spec-compliant submission CSV.

Header: candidate_id,rank,score,reasoning
Exactly 100 data rows; ranks 1..100 unique; score non-increasing with rank;
ties broken by candidate_id ascending; reasoning grounded & varied.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Dict, List

from . import paths


def _clean(text: str) -> str:
    """Keep reasoning single-line and CSV-safe (the csv module handles quoting)."""
    return " ".join((text or "").split())


def write_submission(ranked: List[Dict], out_path=None) -> Path:
    """Write the top-100 ranking to CSV. `ranked` items need rank/candidate_id/
    score_raw/explanation keys (as produced by the ranker)."""
    out_path = Path(out_path or paths.SUBMISSION_CSV)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = sorted(ranked, key=lambda r: r["rank"])[:100]

    # Enforce monotonic non-increasing score as a final safety net.
    prev = None
    for r in rows:
        s = float(r.get("score_raw", 0.0))
        if prev is not None and s > prev:
            s = prev
        r["_score_out"] = s
        prev = s

    with open(out_path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["candidate_id", "rank", "score", "reasoning"])
        for r in rows:
            w.writerow([
                r["candidate_id"],
                r["rank"],
                f"{r['_score_out']:.4f}",
                _clean(r.get("explanation", "")),
            ])
    return out_path


def write_ranked_json(ranked: List[Dict], out_path=None) -> Path:
    """Persist the full explainable ranking for the dashboard/backend."""
    out_path = Path(out_path or paths.RANKED_JSON)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(ranked, f, ensure_ascii=False, indent=2)
    return out_path
