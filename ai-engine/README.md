# ai-engine — Phases 2 & 3 (offline pre-computation)

Builds the structured job profile and the semantic artifacts the ranker uses.

```bash
python ai-engine/analyze_job.py        # JD -> artifacts/job_profile.json + JD embedding
python ai-engine/build_embeddings.py   # all-MiniLM-L6-v2 over the candidate pool
python ai-engine/build_index.py        # FAISS index over the cached embeddings
```

Artifacts written to `../artifacts/`:
- `job_profile.json` — structured JD (required/preferred skills, disqualifiers…)
- `job_embedding.npy` — JD vector for cosine similarity
- `candidate_embeddings.npy` + `candidate_ids.json` — candidate vectors
- `candidates.faiss` — FAISS index for "find similar candidates"

These run **offline** (pre-computation may exceed the 5-min ranking budget). The
ranking step then loads the cached vectors, keeping it CPU-only and < 5 minutes.
Model: `all-MiniLM-L6-v2` (384-dim), cosine similarity via normalized dot product.
