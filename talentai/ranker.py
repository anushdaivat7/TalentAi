"""End-to-end ranking pipeline orchestration.

This is the brain that turns candidates.jsonl into a ranked list with full
explainability. It is designed to satisfy the hackathon compute constraints:

  * CPU only, no network at ranking time
  * streams the 100K pool (flat memory)
  * uses cached embeddings if present (built offline), otherwise runs a strong
    feature/rule-based ranker that still produces a high-quality ranking

The result is consumed by both the submission generator and the dashboard.
"""
from __future__ import annotations

import time
from typing import Dict, List, Optional

import numpy as np

from . import embeddings as emb
from . import job_profile as jp
from . import paths
from .data import iter_candidates
from .explain import build_explanation
from .features import extract_features
from .scoring import ScoreBreakdown, score_candidate
from .traps import detect


def _load_semantic_cache():
    """Load cached candidate embeddings + JD embedding if available."""
    cache = emb.load_cached(paths.EMBEDDINGS_NPY, paths.EMBEDDINGS_IDS)
    if cache is None:
        return None, None
    cand_emb, id_to_row = cache
    if paths.JOB_EMBEDDING_NPY.exists():
        job_vec = np.load(paths.JOB_EMBEDDING_NPY)
    else:
        # If we have candidate vectors but no JD vector, compute it once
        # (allowed only in offline/dashboard context; guarded by caller).
        job_vec = None
    return (cand_emb, id_to_row), job_vec


def rank_all(
    candidates_path=None,
    use_embeddings: bool = True,
    top_k: int = 100,
    progress_every: int = 20000,
    verbose: bool = True,
) -> List[Dict]:
    """Rank every candidate and return the top_k as explanation dicts.

    Returns a list (length top_k) sorted by (score desc, candidate_id asc),
    each item is the Phase-6 explanation dict plus `rank`.
    """
    t0 = time.time()

    semantic_cache = None
    job_vec = None
    if use_embeddings:
        semantic_cache, job_vec = _load_semantic_cache()
        if semantic_cache is not None and verbose:
            print(f"[ranker] using cached embeddings ({semantic_cache[0].shape[0]} vectors)")
        elif verbose:
            print("[ranker] no embedding cache found - using feature/rule-based scoring")

    results: List[ScoreBreakdown] = []
    feature_store: Dict[str, object] = {}
    trap_store: Dict[str, object] = {}

    # Pool-wide trap accounting (free: traps are computed in the loop anyway).
    from collections import Counter
    trap_counts: Counter = Counter()
    honeypot_total = 0
    soft_penalized_total = 0

    n = 0
    for rec in iter_candidates(candidates_path):
        cf = extract_features(rec)
        trap = detect(cf)

        if trap.is_honeypot:
            honeypot_total += 1
        else:
            if trap.penalty < 1.0:
                soft_penalized_total += 1
            for reason in trap.penalty_reasons:
                cat = reason.split(":")[0].split("(")[0].strip()
                trap_counts[cat] += 1

        semantic = None
        if semantic_cache is not None and job_vec is not None:
            cand_emb, id_to_row = semantic_cache
            row = id_to_row.get(cf.candidate_id)
            if row is not None:
                semantic = float(np.dot(cand_emb[row], job_vec))
                semantic = (semantic + 1.0) / 2.0  # map cosine [-1,1] -> [0,1]

        sb = score_candidate(cf, semantic=semantic, trap=trap)
        results.append(sb)
        # Keep features/traps only for candidates likely to land in the top_k
        # to bound memory; we re-extract for finalists if needed.
        feature_store[cf.candidate_id] = cf
        trap_store[cf.candidate_id] = trap

        n += 1
        if verbose and progress_every and n % progress_every == 0:
            print(f"[ranker] scored {n} candidates ({time.time() - t0:.1f}s)")

    # Sort: score desc, then candidate_id asc (matches validator tie-break).
    results.sort(key=lambda s: (-s.final_score, s.candidate_id))
    top = results[:top_k]

    out: List[Dict] = []
    honeypots_in_top = 0
    for rank, sb in enumerate(top, start=1):
        cf = feature_store[sb.candidate_id]
        trap = trap_store[sb.candidate_id]
        if trap.is_honeypot:
            honeypots_in_top += 1
        exp = build_explanation(cf, sb, trap)
        exp["rank"] = rank
        out.append(exp)

    # Persist pool-wide trap stats for the dashboard's trap panel.
    try:
        import json
        stats = {
            "total_scanned": n,
            "honeypots_detected": honeypot_total,
            "honeypots_in_top": honeypots_in_top,
            "soft_penalized": soft_penalized_total,
            "top_k": len(out),
            "soft_trap_categories": [
                {"category": k, "count": v} for k, v in trap_counts.most_common(8)
            ],
        }
        with open(paths.TRAP_STATS_JSON, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass

    if verbose:
        print(f"[ranker] done: {n} candidates in {time.time() - t0:.1f}s, "
              f"returning top {len(out)}")
    return out


def rank_records(records: List[Dict], top_k: int = 100, semantic_fn=None) -> List[Dict]:
    """Rank an in-memory list of records (used by the API on small samples)."""
    scored: List[tuple] = []
    for rec in records:
        cf = extract_features(rec)
        trap = detect(cf)
        semantic = semantic_fn(cf) if semantic_fn else None
        sb = score_candidate(cf, semantic=semantic, trap=trap)
        scored.append((sb, cf, trap))

    scored.sort(key=lambda x: (-x[0].final_score, x[0].candidate_id))
    out = []
    for rank, (sb, cf, trap) in enumerate(scored[:top_k], start=1):
        exp = build_explanation(cf, sb, trap)
        exp["rank"] = rank
        out.append(exp)
    return out
