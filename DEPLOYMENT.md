# Deployment Guide — TalentAI

This guide covers local Docker, MongoDB Atlas, Gemini, and the **mandatory
sandbox link** (Hugging Face Spaces / Streamlit / Colab / Docker).

---

## 1. Local — Docker Compose (full stack)

```bash
# 1. Produce the ranking artifacts on the host first (so they're baked in)
python rank.py --candidates ./.../candidates.jsonl --out ./results/submission.csv
python ai-engine/analyze_job.py            # writes artifacts/job_profile.json

# 2. Bring up backend + frontend
docker compose up --build
# frontend -> http://localhost:8080
# backend  -> http://localhost:8000/docs
```

Environment variables (optional) read by compose: `MONGODB_URI`, `MONGODB_DB`,
`GEMINI_API_KEY`. Put them in a `.env` next to `docker-compose.yml`.

---

## 2. MongoDB Atlas

1. Create a free M0 cluster at <https://cloud.mongodb.com>.
2. Add a database user and allow your IP (or `0.0.0.0/0` for testing).
3. Copy the connection string and export it:
   ```bash
   export MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority"
   ```
4. Ingest:
   ```bash
   python data-ingestion/ingest.py
   ```
   The pipeline validates each record against `candidate_schema.json` and upserts
   into `talentai.candidates` (indexed on `candidate_id`). Without `MONGODB_URI`
   it validates + writes a local snapshot instead, so nothing breaks.

---

## 3. Gemini (explanations — optional, never used during ranking)

```bash
export GEMINI_API_KEY="your-key"      # from https://aistudio.google.com/app/apikey
export GEMINI_MODEL="gemini-1.5-flash"
```
Used only by the dashboard/chatbot to enrich the grounded rule-based
explanations. The Stage-3 ranking step always runs with the network OFF.

---

## 4. Sandbox link (required by the submission portal)

The spec requires a hosted environment that runs your ranker on a small sample.

### Option A — Hugging Face Spaces (Docker)
1. Create a new **Docker** Space.
2. Push this repo; add a top-level `Dockerfile` that runs the backend and serves
   a minimal upload form, or reuse `backend/Dockerfile`.
3. Expose `POST /api/submission/generate` so reviewers can rank a sample.

### Option B — Google Colab
A single notebook that:
```python
!pip install -r requirements.txt
!python rank.py --candidates sample_candidates.jsonl --out submission.csv
```
Share the Colab link (set to "anyone with the link can view").

### Option C — Streamlit Cloud
Wrap `talentai.ranker.rank_records` in a Streamlit app that accepts an uploaded
`≤100`-candidate JSONL and shows the ranked table + downloadable CSV.

> Whatever you pick, it must complete on ≤100 candidates within 5 minutes on CPU.

---

## 5. Stage-3 reproduction contract

The judges reproduce your ranking in a sandboxed container:
**5 min · 16 GB · CPU only · no network.**

TalentAI satisfies this because:
- `rank.py` only needs `numpy` at ranking time (embeddings are precomputed).
- It streams `candidates.jsonl` (flat memory).
- No external/API calls in the ranking path (Gemini is dashboard-only).

Reproduce command (also in `submission_metadata.yaml`):
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv
```

To guarantee the no-embedding fallback (most portable):
```bash
python rank.py --candidates ./candidates.jsonl --out ./submission.csv --no-embeddings
```

---

## 6. Production notes
- Build embeddings/index offline and ship them as artifacts (or a build script).
- For a 200K+ pool, swap `IndexFlatIP` for `IndexIVFFlat`/HNSW in `faiss_index.py`.
- The backend is stateless over `results/ranked_candidates.json`; scale it
  horizontally behind any load balancer.
