"""Phase 1 - Data ingestion pipeline.

Loads candidates.jsonl, validates every record against candidate_schema.json,
and stores the profiles in MongoDB (Atlas or local). MongoDB is optional: if no
MONGODB_URI is configured the pipeline still runs validation and writes a local
JSON snapshot, so the rest of the system works without a database.

Usage:
    python data-ingestion/ingest.py --validate-only
    python data-ingestion/ingest.py --limit 5000
    python data-ingestion/ingest.py            # full ingest into MongoDB
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# Make the `talentai` package importable when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from talentai import paths  # noqa: E402
from talentai.data import iter_candidates  # noqa: E402
from talentai.schema_validation import validate_record  # noqa: E402

BATCH = 1000


def get_collection():
    """Return a MongoDB collection or None if MongoDB is not configured."""
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return None
    try:
        from pymongo import MongoClient

        client = MongoClient(uri, serverSelectionTimeoutMS=8000)
        db = client[os.getenv("MONGODB_DB", "talentai")]
        col = db[os.getenv("MONGODB_COLLECTION", "candidates")]
        col.create_index("candidate_id", unique=True)
        return col
    except Exception as e:  # noqa: BLE001
        print(f"[ingest] WARNING: could not connect to MongoDB: {e}")
        return None


def main() -> int:
    ap = argparse.ArgumentParser(description="TalentAI candidate ingestion")
    ap.add_argument("--candidates", default=None, help="path to candidates.jsonl[.gz]")
    ap.add_argument("--limit", type=int, default=None, help="only ingest N records")
    ap.add_argument("--validate-only", action="store_true", help="validate, do not store")
    ap.add_argument("--strict", action="store_true", help="abort on first invalid record")
    args = ap.parse_args()

    src = Path(args.candidates) if args.candidates else paths.candidates_file()
    print(f"[ingest] source: {src}")

    col = None if args.validate_only else get_collection()
    if col is not None:
        print("[ingest] MongoDB connected - storing profiles")
    elif not args.validate_only:
        print("[ingest] no MongoDB - validation + local snapshot only")

    total = valid = invalid = stored = 0
    batch = []
    snapshot = []

    for rec in iter_candidates(src):
        total += 1
        errs = validate_record(rec)
        if errs:
            invalid += 1
            if invalid <= 10:
                print(f"  invalid {rec.get('candidate_id', '?')}: {errs[0]}")
            if args.strict:
                print("[ingest] aborting (--strict)")
                return 1
        else:
            valid += 1

        if col is not None and not errs:
            batch.append(rec)
            if len(batch) >= BATCH:
                _upsert(col, batch)
                stored += len(batch)
                batch = []
        elif not args.validate_only and len(snapshot) < 2000:
            snapshot.append(rec)

        if args.limit and total >= args.limit:
            break

    if col is not None and batch:
        _upsert(col, batch)
        stored += len(batch)

    if col is None and not args.validate_only and snapshot:
        out = paths.ARTIFACTS / "candidates_snapshot.json"
        import json
        with open(out, "w", encoding="utf-8") as f:
            json.dump(snapshot, f)
        print(f"[ingest] wrote local snapshot ({len(snapshot)} records) -> {out}")

    print(f"\n[ingest] total={total} valid={valid} invalid={invalid} stored={stored}")
    return 0


def _upsert(col, batch):
    from pymongo import UpdateOne

    ops = [UpdateOne({"candidate_id": r["candidate_id"]}, {"$set": r}, upsert=True)
           for r in batch]
    col.bulk_write(ops, ordered=False)


if __name__ == "__main__":
    raise SystemExit(main())
