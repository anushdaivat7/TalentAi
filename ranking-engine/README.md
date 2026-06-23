# ranking-engine — Phases 4–6

Runs the full ranking and writes explainable results.

```bash
python ranking-engine/run_ranking.py                 # uses cached embeddings if present
python ranking-engine/run_ranking.py --no-embeddings # pure feature/rule-based
python ranking-engine/run_ranking.py --candidates path/to/candidates.jsonl
```

Outputs:
- `results/ranked_candidates.json` — full explainability (consumed by the API)
- `results/submission.csv` — spec-compliant top-100

## Scoring

```
base  = 0.40·skill + 0.25·experience + 0.15·project + 0.10·education + 0.10·behavioral
final = base · (0.35 + 0.65·role_fit) · trap_penalty
```

`role_fit` (title + career evidence) is the decisive anti-keyword-stuffer signal;
`trap_penalty` forces honeypots to the bottom and down-weights consulting-only,
job-hopper, research-only, CV/speech-without-NLP and inactive profiles. Sorting is
`(score desc, candidate_id asc)` to match the validator's tie-break rule.
