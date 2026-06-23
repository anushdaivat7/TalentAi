"""Trap-engine diagnostics: counts honeypots and soft-trap categories over the
full candidate pool. Useful for sanity-checking that the integrity heuristics
fire as intended (the dataset is documented to contain ~80 honeypots).

Usage:
    python ranking-engine/diagnostics.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from talentai.data import iter_candidates  # noqa: E402
from talentai.features import extract_features  # noqa: E402
from talentai.traps import detect  # noqa: E402


def main() -> int:
    honeypots = 0
    soft = Counter()
    honeypot_reasons = Counter()
    soft_penalized = 0
    n = 0
    for rec in iter_candidates():
        cf = extract_features(rec)
        t = detect(cf)
        n += 1
        if t.is_honeypot:
            honeypots += 1
            for r in t.honeypot_reasons:
                honeypot_reasons[r.split("(")[0].strip()[:50]] += 1
        elif t.penalty < 1.0:
            soft_penalized += 1
            for r in t.penalty_reasons:
                soft[r.split(":")[0].split("(")[0].strip()[:45]] += 1
        if n % 25000 == 0:
            print(f"  scanned {n} ...")

    print(f"\nscanned: {n}")
    print(f"honeypots detected: {honeypots}")
    print("honeypot reason breakdown:")
    for k, v in honeypot_reasons.most_common():
        print(f"  {v:6d}  {k}")
    print("\ntop soft-trap categories:")
    for k, v in soft.most_common(10):
        print(f"  {v:6d}  {k}")

    # Persist a stats file the dashboard's trap panel consumes.
    import json
    from talentai import paths  # noqa: E402

    honeypots_in_top = 0
    try:
        ranked = json.loads(paths.RANKED_JSON.read_text(encoding="utf-8"))
        honeypots_in_top = sum(1 for r in ranked if r.get("is_honeypot"))
    except Exception:
        pass

    stats = {
        "total_scanned": n,
        "honeypots_detected": honeypots,
        "honeypots_in_top": honeypots_in_top,
        "soft_penalized": soft_penalized,
        "top_k": 100,
        "soft_trap_categories": [
            {"category": k, "count": v} for k, v in soft.most_common(8)
        ],
    }
    paths.TRAP_STATS_JSON.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(f"\nwrote {paths.TRAP_STATS_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
