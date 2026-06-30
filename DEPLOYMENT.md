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



## 6. Production notes
- Build embeddings/index offline and ship them as artifacts (or a build script).
- For a 200K+ pool, swap `IndexFlatIP` for `IndexIVFFlat`/HNSW in `faiss_index.py`.
- The backend is stateless over `results/ranked_candidates.json`; scale it
  horizontally behind any load balancer.
