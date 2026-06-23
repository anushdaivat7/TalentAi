"""Phase 9 - Submission generator + validator.

Builds the final CSV from results/ranked_candidates.json (or by running the
ranker if no results exist yet), names it after the participant/team id, and
runs the official validate_submission.py against it.

Usage:
    python submission-generator/generate.py --team team_talentai
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from talentai import paths  # noqa: E402
from talentai.submission import write_submission  # noqa: E402


def _load_validator():
    vp = paths.bundle_dir() / "validate_submission.py"
    if not vp.exists():
        return None
    spec = importlib.util.spec_from_file_location("validate_submission", vp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate & validate the submission CSV")
    ap.add_argument("--team", default="team_talentai", help="participant/team id (filename)")
    ap.add_argument("--ranked", default=None, help="path to ranked_candidates.json")
    ap.add_argument("--out-dir", default=str(paths.RESULTS))
    args = ap.parse_args()

    ranked_path = Path(args.ranked) if args.ranked else paths.RANKED_JSON
    if not ranked_path.exists():
        print("[generate] no ranked results found - running the ranker first ...")
        from talentai.ranker import rank_all
        from talentai.submission import write_ranked_json

        ranked = rank_all()
        write_ranked_json(ranked)
    else:
        with open(ranked_path, "r", encoding="utf-8") as f:
            ranked = json.load(f)

    out_path = Path(args.out_dir) / f"{args.team}.csv"
    write_submission(ranked, out_path=out_path)
    print(f"[generate] wrote submission -> {out_path}")

    validator = _load_validator()
    if validator is None:
        print("[generate] validator not found in bundle; skipping validation")
        return 0

    errors = validator.validate_submission(str(out_path))
    if errors:
        print(f"[generate] VALIDATION FAILED ({len(errors)} issue(s)):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("[generate] Submission is valid. [OK]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
