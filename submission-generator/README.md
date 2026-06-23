# submission-generator — Phase 9

Builds the final CSV and validates it with the **official** `validate_submission.py`.

```bash
python submission-generator/generate.py --team team_talentai
```

- Reads `results/ranked_candidates.json` (or runs the ranker if missing).
- Writes `results/<team>.csv` with header `candidate_id,rank,score,reasoning`,
  exactly 100 rows, ranks 1–100 unique, score non-increasing, ties broken by
  `candidate_id` ascending.
- Runs the bundled validator and prints PASS/FAIL with specific errors.

The API exposes the same flow at `POST /api/submission/generate`,
`GET /api/submission/validate` and `GET /api/submission/download`.
