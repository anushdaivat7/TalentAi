"""Phase 3 - Pre-compute candidate embeddings (OFFLINE).

Generates all-MiniLM-L6-v2 embeddings for every candidate and caches them to
artifacts/. This is the pre-computation step that lets the ranking step stay
within the 5-minute, no-network budget (the ranker just loads these vectors).

Usage:
    python ai-engine/build_embeddings.py                # full pool
    python ai-engine/build_embeddings.py --limit 5000   # quick test
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from talentai import paths  # noqa: E402
from talentai.data import iter_candidates  # noqa: E402
from talentai.features import extract_features  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Build candidate embedding cache")
    ap.add_argument("--candidates", default=None)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=256)
    args = ap.parse_args()

    import numpy as np
    from talentai import embeddings as emb

    src = Path(args.candidates) if args.candidates else paths.candidates_file()
    print(f"[build_embeddings] source: {src}")
    print(f"[build_embeddings] loading model {emb.MODEL_NAME} ...")
    emb.get_model()

    ids, texts = [], []
    all_vecs = []
    t0 = time.time()
    flushed = 0

    def flush():
        nonlocal flushed
        if not texts:
            return
        vecs = emb.embed_texts(texts, batch_size=args.batch_size, show_progress=False)
        all_vecs.append(vecs)
        flushed += len(texts)
        texts.clear()
        print(f"[build_embeddings] embedded {flushed} ({time.time() - t0:.1f}s)")

    n = 0
    for rec in iter_candidates(src):
        cf = extract_features(rec)
        ids.append(cf.candidate_id)
        texts.append(cf.embedding_text)
        n += 1
        if len(texts) >= 10000:
            flush()
        if args.limit and n >= args.limit:
            break
    flush()

    matrix = np.vstack(all_vecs)
    np.save(paths.EMBEDDINGS_NPY, matrix)
    with open(paths.EMBEDDINGS_IDS, "w", encoding="utf-8") as f:
        json.dump(ids, f)
    print(f"[build_embeddings] saved {matrix.shape} -> {paths.EMBEDDINGS_NPY}")
    print(f"[build_embeddings] saved {len(ids)} ids -> {paths.EMBEDDINGS_IDS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
