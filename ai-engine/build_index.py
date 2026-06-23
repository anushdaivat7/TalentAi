"""Phase 3 - Build a FAISS index over the cached candidate embeddings (OFFLINE).

Powers semantic "find similar candidates" search in the dashboard. Run after
build_embeddings.py.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from talentai import paths  # noqa: E402


def main() -> int:
    import numpy as np
    from talentai import faiss_index as fi

    if not paths.EMBEDDINGS_NPY.exists():
        print("[build_index] no embeddings cache - run build_embeddings.py first")
        return 1

    emb = np.load(paths.EMBEDDINGS_NPY)
    print(f"[build_index] building FAISS index over {emb.shape} ...")
    index = fi.build_index(emb)
    fi.save_index(index, paths.FAISS_INDEX)
    print(f"[build_index] saved -> {paths.FAISS_INDEX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
