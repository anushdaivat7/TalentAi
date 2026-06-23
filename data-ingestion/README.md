# data-ingestion — Phase 1

Loads `candidates.jsonl`, validates every record against `candidate_schema.json`,
and stores valid profiles in MongoDB.

```bash
python data-ingestion/ingest.py --validate-only      # just validate
python data-ingestion/ingest.py --limit 5000         # ingest a subset
python data-ingestion/ingest.py                       # full ingest -> MongoDB
```

- Uses `jsonschema` (draft-07) when installed; otherwise a lightweight structural
  check so ingestion never hard-fails.
- Requires `MONGODB_URI` to store in Atlas; without it, validates and writes a
  local snapshot to `artifacts/candidates_snapshot.json`.
- Streams the file, so the 100K / ~465 MB pool ingests with flat memory.
