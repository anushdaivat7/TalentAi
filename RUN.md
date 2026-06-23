# TalentAI — How to Run (Step by Step)

This is the complete, copy‑paste guide to run the whole project: the **ranking
engine** (produces `submission.csv`) and the **web app** (FastAPI backend +
React dashboard).

Commands are written for **Windows PowerShell** (the project's environment).
macOS/Linux equivalents are noted where they differ.

---

## 0. Prerequisites

| Tool | Version | Check |
|------|---------|-------|
| Python | 3.10+ | `python --version` |
| Node.js | 18+ | `node --version` |
| npm | 9+ | `npm --version` |

The challenge data bundle must be present at:

```
[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl
```

> The ranker auto‑finds it. To point elsewhere, set `TALENTAI_CANDIDATES` to the
> file path (or `TALENTAI_BUNDLE` to the folder).

---

## 1. One‑time setup

Open a terminal in the project root: `C:\Users\Lenovo\Desktop\TalentAI`

### 1a. Python virtual environment (recommended)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> macOS/Linux: `python3 -m venv .venv && source .venv/bin/activate`

### 1b. Install Python dependencies

```powershell
# Core engine + tests + (optional) AI extras
python -m pip install -r requirements.txt

# Backend API dependencies
python -m pip install -r backend\requirements.txt
```

> Only `numpy` is strictly required to reproduce `submission.csv`. The rest power
> the API, dashboard, optional embeddings, MongoDB and Gemini.

### 1c. Install frontend dependencies

```powershell
cd frontend
npm install
cd ..
```

---

## 2. Run the ranking engine (produces the submission)

This reads all 100k candidates, scores them, and writes the outputs.

```powershell
python ranking-engine\run_ranking.py --no-embeddings
```

Outputs created:

- `results\ranked_candidates.json` — full explainability (used by the dashboard)
- `results\submission.csv` — the spec‑compliant top‑100
- `results\trap_stats.json` — pool‑wide honeypot/trap stats (used by the dashboard)

> `--no-embeddings` uses the fast, strong rule‑based ranker and always finishes
> within the compute budget. Drop the flag only if you've pre‑built the embedding
> cache (see Section 6).

### Reproduce exactly (Stage‑3 style, single command)

```powershell
python rank.py --candidates ".\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl" --out .\submission.csv --no-embeddings
```

### Generate + validate the named submission file

```powershell
python submission-generator\generate.py --team team_talentai
```

This writes the team‑named CSV and runs the official validator.

---

## 3. Run the backend API (FastAPI)

In a terminal (with the venv activated):

```powershell
cd backend
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
```

- API base: `http://127.0.0.1:8000`
- Interactive docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/api/health`

> Keep this terminal open. Use `--reload` during development to auto‑restart on
> code changes. If you re‑run the ranker while the server is up, refresh its data
> with a `POST http://127.0.0.1:8000/api/reload`.

---

## 4. Run the frontend (React dashboard)

In a **second** terminal:

```powershell
cd frontend
npm run dev
```

Open the dashboard at: **http://localhost:5173**

The dev server proxies `/api` calls to the backend on `127.0.0.1:8000`, so make
sure the backend (Section 3) is running first.

What you'll see on the dashboard:

- Summary stat cards
- **Stacked score‑breakdown chart** (top 10) — proves the scoring logic
- Ranking / skill / experience / education charts (**click a bar to filter the table**)
- **Integrity & Trap panel** — honeypots disqualified + soft‑trap categories
- Candidate table with search, filters and detail modal
- AI Chatbot, Job Profile and Submission tabs

---

## 5. Quick start (TL;DR)

```powershell
# from project root, venv activated, deps installed
python ranking-engine\run_ranking.py --no-embeddings        # 1) rank

# Terminal A
cd backend; python -m uvicorn app.main:app --port 8000 --host 127.0.0.1

# Terminal B
cd frontend; npm run dev                                      # open http://localhost:5173
```

---

## 6. Optional steps

### 6a. Tests

```powershell
python -m pytest -q
```

### 6b. Trap diagnostics (regenerates `results\trap_stats.json`)

```powershell
python ranking-engine\diagnostics.py
```

### 6c. Embeddings + FAISS (offline, CPU‑heavy — optional)

Only needed if you want semantic‑embedding ranking instead of the rule‑based path.
This can take a long time on a laptop CPU.

```powershell
python ai-engine\analyze_job.py          # builds artifacts\job_profile.json (+ JD embedding)
python ai-engine\build_embeddings.py     # builds artifacts\candidate_embeddings.npy
python ai-engine\build_index.py          # builds artifacts\candidates.faiss
python ranking-engine\run_ranking.py     # now uses the embedding cache (no --no-embeddings)
```

### 6d. Run everything with Docker

```powershell
docker-compose up --build
```

- Frontend: `http://localhost:8080` (or the port mapped in `docker-compose.yml`)
- Backend: `http://localhost:8000`

### 6e. Optional environment variables

Copy `.env.example` to `.env` and fill in as needed:

- `GEMINI_API_KEY` — enables richer AI explanations/chatbot (falls back to
  rule‑based answers if absent)
- `MONGODB_URI` — enables MongoDB storage (pipeline degrades gracefully without it)
- `TALENTAI_CANDIDATES` / `TALENTAI_BUNDLE` — point the ranker at custom data

---

## 7. Troubleshooting

| Symptom | Fix |
|--------|-----|
| `WinError 10013` on backend start | Port 8000 in use. Find/kill it: `netstat -ano \| findstr :8000` then `Stop-Process -Id <PID> -Force`, or use `--port 8001`. |
| Frontend shows `ECONNREFUSED ::1:8000` | Start the backend first; the proxy targets IPv4 `127.0.0.1` (already configured). |
| Dashboard says "No ranking loaded" | Run Section 2, then `POST /api/reload` (or restart the backend). |
| `ModuleNotFoundError: talentai` | Run commands from the project root with the venv activated. |
| Trap panel numbers missing | Run `python ranking-engine\diagnostics.py` to (re)create `results\trap_stats.json`. |

---

*TalentAI · Redrob India Runs Data & AI Challenge*
