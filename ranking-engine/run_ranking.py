"""Phases 4-6 - Run the full ranking and write explainable results.

Produces results/ranked_candidates.json (full explainability for the dashboard)
and results/submission.csv (the spec-compliant top-100). This is the heart of
the system and respects the compute constraints (CPU, no network, streaming).

Usage:
    python ranking-engine/run_ranking.py
    python ranking-engine/run_ranking.py --no-embeddings --candidates path.jsonl
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from talentai import paths  # noqa: E402
from talentai.ranker import rank_all  # noqa: E402
from talentai.submission import write_ranked_json, write_submission  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the TalentAI ranking pipeline")
    ap.add_argument("--candidates", default=None, help="candidates.jsonl[.gz]")
    ap.add_argument("--out", default=None, help="submission CSV path")
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--no-embeddings", action="store_true",
                    help="force feature/rule-based ranking (skip embedding cache)")
    args = ap.parse_args()

    t0 = time.time()
    ranked = rank_all(
        candidates_path=Path(args.candidates) if args.candidates else None,
        use_embeddings=not args.no_embeddings,
        top_k=args.top_k,
    )

    json_path = write_ranked_json(ranked)
    csv_path = write_submission(ranked, out_path=args.out)

    print(f"\n[run_ranking] wrote {json_path}")
    print(f"[run_ranking] wrote {csv_path}")
    print(f"[run_ranking] total wall-clock: {time.time() - t0:.1f}s")

    print("\nTop 10:")
    for r in ranked[:10]:
        print(f"  #{r['rank']:>3}  {r['candidate_id']}  "
              f"{r['final_score']:.1f}  {r['explanation'][:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
