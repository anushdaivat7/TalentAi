"""Sentence-Transformers (all-MiniLM-L6-v2) wrapper.

Embeddings are computed OFFLINE (pre-computation step) and cached to disk, so
the ranking step that produces the submission CSV stays within the 5-minute,
no-network compute budget. The ranker loads the cached vectors; it never needs
the model or the network at ranking time.
"""
from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

import numpy as np

MODEL_NAME = "all-MiniLM-L6-v2"
DIM = 384


@lru_cache(maxsize=1)
def get_model(model_name: str = MODEL_NAME):
    """Load the sentence-transformers model (downloads once, then cached)."""
    from sentence_transformers import SentenceTransformer  # lazy import

    return SentenceTransformer(model_name)


def embed_texts(texts: List[str], batch_size: int = 256, show_progress: bool = True) -> np.ndarray:
    """Return L2-normalized embeddings (cosine == dot product)."""
    model = get_model()
    vecs = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return vecs.astype("float32")


def embed_one(text: str) -> np.ndarray:
    return embed_texts([text], show_progress=False)[0]


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity for already- or not-yet-normalized vectors."""
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def load_cached(npy_path, ids_path) -> Optional[tuple]:
    """Load cached (embeddings, id->row index) if present, else None."""
    import json
    from pathlib import Path

    npy_path, ids_path = Path(npy_path), Path(ids_path)
    if not (npy_path.exists() and ids_path.exists()):
        return None
    emb = np.load(npy_path)
    with open(ids_path, "r", encoding="utf-8") as f:
        ids = json.load(f)
    id_to_row = {cid: i for i, cid in enumerate(ids)}
    return emb, id_to_row
