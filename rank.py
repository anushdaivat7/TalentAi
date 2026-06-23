"""TalentAI - single reproduce command (Stage-3 entrypoint).

Produces a spec-compliant submission CSV from a candidates file, end-to-end,
on CPU with no network access. Uses the cached embeddings in artifacts/ if they
exist (built offline via ai-engine/build_embeddings.py); otherwise it falls back
to the strong feature/rule-based ranker so it always completes within budget.

Usage (matches submission_metadata.yaml):
    python rank.py --candidates ./candidates.jsonl --out ./submission.csv
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from talentai.ranker import rank_all
from talentai.submission import write_ranked_json, write_submission


def main() -> int:
    ap = argparse.ArgumentParser(description="TalentAI ranker - produce submission.csv")
    ap.add_argument("--candidates", required=True, help="path to candidates.jsonl[.gz]")
    ap.add_argument("--out", default="submission.csv", help="output CSV path")
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--no-embeddings", action="store_true",
                    help="force feature/rule-based ranking")
    args = ap.parse_args()

    t0 = time.time()
    ranked = rank_all(
        candidates_path=Path(args.candidates),
        use_embeddings=not args.no_embeddings,
        top_k=args.top_k,
    )
    write_ranked_json(ranked)
    out = write_submission(ranked, out_path=args.out)
    print(f"[rank] wrote {out} in {time.time() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
