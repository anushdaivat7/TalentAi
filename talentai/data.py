"""Candidate data loading utilities (streaming, memory-friendly)."""
from __future__ import annotations

import gzip
import json
from pathlib import Path
from typing import Dict, Iterator, List, Optional

from . import paths


def _open(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def iter_candidates(path: Optional[Path] = None) -> Iterator[Dict]:
    """Yield candidate dicts one at a time from a .jsonl or .jsonl.gz file.

    Streaming keeps memory flat even for the 100K / ~465 MB pool.
    """
    path = path or paths.candidates_file()
    with _open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def load_candidates(path: Optional[Path] = None, limit: Optional[int] = None) -> List[Dict]:
    """Load candidates into a list (use `limit` for quick experiments)."""
    out: List[Dict] = []
    for i, c in enumerate(iter_candidates(path)):
        if limit is not None and i >= limit:
            break
        out.append(c)
    return out


def count_candidates(path: Optional[Path] = None) -> int:
    return sum(1 for _ in iter_candidates(path))
