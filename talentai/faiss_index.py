"""FAISS vector index helpers for semantic candidate search.

Built offline alongside the embeddings cache and used by the backend for
"find similar candidates" / semantic search in the dashboard. The submission
ranker does not require FAISS (it uses the cached cosine similarities directly),
keeping the ranking step dependency-light.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np


def build_index(embeddings: np.ndarray):
    """Build an inner-product FAISS index over L2-normalized vectors."""
    import faiss  # lazy import

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(np.ascontiguousarray(embeddings.astype("float32")))
    return index


def save_index(index, path) -> None:
    import faiss

    faiss.write_index(index, str(path))


def load_index(path) -> Optional["object"]:
    import faiss

    path = Path(path)
    if not path.exists():
        return None
    return faiss.read_index(str(path))


def search(index, query: np.ndarray, k: int = 10) -> Tuple[List[int], List[float]]:
    """Return (row_indices, scores) of the top-k most similar vectors."""
    q = np.ascontiguousarray(query.reshape(1, -1).astype("float32"))
    scores, idx = index.search(q, k)
    return idx[0].tolist(), scores[0].tolist()
