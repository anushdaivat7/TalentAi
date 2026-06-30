# 🚀 TalentAI — Intelligent Candidate Discovery & Ranking

An end-to-end, **explainable AI ranking engine** for the **Redrob India Runs Data & AI Challenge**. It ranks the top **100** candidates from a **100,000**-profile pool for the **Senior AI Engineer** role — going beyond keyword matching with semantic understanding, trap/honeypot detection, and grounded per-candidate reasoning.

```
candidates.jsonl (100K)  ──►  feature extraction + traps + semantic match
                                        │
                          5 component scores × role-fit × trap penalty
                                        │
                         ┌──────────────┴───────────────┐
                         ▼                              ▼
              submission.csv (top 100)        ranked_candidates.json
              (spec-compliant, validated)     (full explainability)
                         │                              │
                         ▼                              ▼
                  Stage-1 validator            FastAPI + React dashboard
```

---

## 🔑 Features

- **Hybrid explainable ranker** — Skill (40%) · Experience (25%) · Project (15%) · Education (10%) · Behavioral (10%), modulated by role-fit and trap penalties
- **Honeypot & trap detection** — 40 impossible profiles disqualified; soft penalties for keyword-stuffers, consulting-only careers, job-hoppers, and more
- **Discovery pipeline dashboard** — 100K → integrity check → red-flag filter → Top 100 shortlist
- **Interactive recruiter UI** — stacked score chart, skill coverage, trap panel, searchable candidate table, detail pages
- **AI chatbot** — rule-based recruiter Q&A (optional Gemini enrichment)
- **Submission generator** — spec-compliant CSV + PDF report, validated with official `validate_submission.py`
- **Reproducible** — single command: `python rank.py …` (CPU-only, no network, &lt; 5 min)

---

## 🌐 Live Demo & Links

> Replace the placeholder URLs below with your real links before submission.

| Link | URL |
|------|-----|
| **GitHub Repo** | [github.com/anushdaivat7/TalentAi](https://github.com/anushdaivat7/TalentAi) |
| **Sandbox (ranker demo)** | [https://main.d67xcwttv5bl7.amplifyapp.com/] |
| **Frontend (local)** | [http://localhost:5173](http://localhost:5173) |
| **Backend API (local)** | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| **API Docs (Swagger)** | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |
| **Health check** | [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) |

📄 **Full step-by-step guide:** [RUN.md](./RUN.md)

---

## 🛠️ Tech Stack

| Layer | Technologies |
|-------|--------------|
| **Ranking engine** | Python, NumPy, sentence-transformers (optional), FAISS (optional) |
| **Backend** | FastAPI, Uvicorn, Pydantic, ReportLab |
| **Frontend** | React, Vite, Tailwind CSS, Recharts, React Router |
| **Data** | JSONL streaming, jsonschema, MongoDB (optional) |
| **Deploy** | Docker, docker-compose, Nginx |

---

## 📦 Dataset setup (for judges & reviewers)

This repo contains **code only** — not the official 100K candidate pool (too large for GitHub).  
Judges and reviewers already receive the **Redrob challenge bundle** separately. You only need to point the ranker at `candidates.jsonl`.

### Step 1 — Get the official data

Use the challenge bundle you received from Redrob. You need at least:

```
candidates.jsonl          # full pool (~100,000 profiles) — required for final submission
candidate_schema.json     # optional, for validation
validate_submission.py    # optional, used by submission-generator/
```

### Step 2 — Place the file (pick one option)

**Option A — project root (simplest for judges)**

Copy `candidates.jsonl` next to `rank.py`:

```
TalentAi/
├── rank.py
├── candidates.jsonl    ← put file here
├── talentai/
└── ...
```

**Option B — keep bundle folder locally (Windows example)**

```
TalentAi/
├── [PUB] India_runs_data_and_ai_challenge/
│   └── India_runs_data_and_ai_challenge/
│       └── candidates.jsonl
└── rank.py
```

The ranker auto-finds this path if the folder exists locally.

**Option C — custom path (any OS)**

```powershell
# Windows PowerShell
$env:TALENTAI_CANDIDATES = "C:\path\to\candidates.jsonl"
```

```bash
# macOS / Linux
export TALENTAI_CANDIDATES=/path/to/candidates.jsonl
```

No code changes needed — only the data path.

### Step 3 — Reproduce submission (Stage 3 command)

From project root, with venv activated and `pip install -r requirements.txt`:

```powershell
python rank.py --candidates ./candidates.jsonl --out ./submission.csv --no-embeddings
```

Or with the local bundle path:

```powershell
python rank.py --candidates ".\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl" --out .\submission.csv --no-embeddings
```

Expected: finishes in a few minutes on CPU, writes `submission.csv` (100 rows).

### Step 4 — Validate output

```powershell
python submission-generator\generate.py --team team_Talentai
```

### Step 5 — Load dashboard (optional)

After ranking, start backend + frontend (see [Quick Start](#-quick-start-all-commands)).  
If the backend was already running, refresh data with:

```
POST http://127.0.0.1:8000/api/reload
```

> **Note:** The dataset is **not** committed to GitHub on purpose. Cloning this repo always requires placing `candidates.jsonl` locally (one step). Organizers provide the same file for Stage-3 evaluation.

---

## ⚡ Quick Start (all commands)

**Prerequisites:** Python 3.10+, Node.js 18+, and `candidates.jsonl` from the official challenge bundle (see [Dataset setup](#-dataset-setup-for-judges--reviewers) above).

### 1️⃣ One-time setup

```powershell
# Windows PowerShell — from project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r backend\requirements.txt
cd frontend; npm install; cd ..
```

```bash
# macOS / Linux
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..
```

### 2️⃣ Run ranking (produces submission + dashboard data)

```powershell
python ranking-engine\run_ranking.py --no-embeddings
```

Creates:
- `results/ranked_candidates.json` — explainability for dashboard
- `results/submission.csv` — top 100
- `results/trap_stats.json` — honeypot/trap stats

**Stage-3 reproduce command (single line):**

```powershell
python rank.py --candidates ".\[PUB] India_runs_data_and_ai_challenge\India_runs_data_and_ai_challenge\candidates.jsonl" --out .\submission.csv --no-embeddings
```

**Generate + validate team CSV:**

```powershell
python submission-generator\generate.py --team team_Talentai
```

### 3️⃣ Run backend (Terminal A)

```powershell
cd backend
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
```

- API: http://127.0.0.1:8000  
- Docs: http://127.0.0.1:8000/docs  

After re-ranking while server is up: `POST http://127.0.0.1:8000/api/reload`

### 4️⃣ Run frontend (Terminal B)

```powershell
cd frontend
npm run dev
```

Open: **http://localhost:5173**

### 5️⃣ TL;DR — three commands

```powershell
python ranking-engine\run_ranking.py --no-embeddings
cd backend; python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
cd frontend; npm run dev
```

### 6️⃣ Tests

```powershell
python -m pytest -q
```

### 7️⃣ Docker (optional)

```powershell
docker-compose up --build
```

### 8️⃣ Optional: trap diagnostics / embeddings

```powershell
python ranking-engine\diagnostics.py          # regenerate trap_stats.json
python ai-engine\analyze_job.py               # job profile (optional)
python ai-engine\build_embeddings.py          # CPU-heavy, optional
python ai-engine\build_index.py               # FAISS index, optional
```

---

## 🏆 Why this ranker wins

| Trap in the dataset | How TalentAI handles it |
| --- | --- |
| **Keyword stuffers** | Decisive **role-fit** multiplier (title + career evidence) |
| **Honeypots** (~80 in dataset) | Hard integrity checks → **40 disqualified**, rest via soft penalties |
| **Plain-language fits** | Career-evidence concept matching, not buzzword-only |
| **Consulting-only / job-hoppers** | Graded soft-trap penalties |
| **Inactive / unavailable** | Behavioral availability modifier |

**Compute-safe:** ranking runs **CPU-only, no network, &lt; 5 minutes** on 100K profiles.

---

## 📐 Ranking formula

```
base   = 0.40·skill + 0.25·experience + 0.15·project + 0.10·education + 0.10·behavioral
final  = base · (0.35 + 0.65·role_fit) · trap_penalty        # 0..1, scaled to 0..100 in UI
```

---

## 📁 Project structure

```
TalentAI/
├── talentai/                # Core library (ranking brain)
├── ranking-engine/          # run_ranking.py, diagnostics.py
├── ai-engine/               # analyze_job, build_embeddings, build_index
├── submission-generator/    # generate.py + validator
├── backend/                 # FastAPI API
├── frontend/                # React dashboard
├── rank.py                  # Stage-3 reproduce entrypoint
├── RUN.md                   # Full run guide (Windows-focused)
├── submission_metadata.yaml # Hackathon submission metadata
└── docker-compose.yml
```

---

## 🔌 API surface (FastAPI)

| Endpoint | Purpose |
| --- | --- |
| `GET /api/health` | Status + ranked count |
| `GET /api/dashboard/summary` | Stat cards |
| `GET /api/dashboard/charts` | Score breakdown + skill coverage |
| `GET /api/dashboard/trap-stats` | Discovery / trap pipeline stats |
| `GET /api/candidates` | Search / filter ranked list |
| `GET /api/candidates/{id}` | Full explainability + raw profile |
| `POST /api/chat` | AI recruiter chatbot |
| `POST /api/submission/generate` | Generate CSV |
| `GET /api/submission/validate` | Run official validator |
| `GET /api/submission/download` | Download CSV |
| `GET /api/submission/report.pdf` | Download PDF ranking report |

---

## 🐛 Troubleshooting

| Symptom | Fix |
|--------|-----|
| Port 8000 busy (`WinError 10013`) | `netstat -ano \| findstr :8000` then `Stop-Process -Id <PID> -Force` |
| Frontend `ECONNREFUSED ::1:8000` | Start backend first; proxy uses `127.0.0.1` |
| Dashboard: "No ranking loaded" | Run ranking, then `POST /api/reload` or restart backend |
| Trap panel empty | `python ranking-engine\diagnostics.py` |

More details: **[RUN.md](./RUN.md)** · **[DEPLOYMENT.md](./DEPLOYMENT.md)**

---

## 👥 Team

**team_Talentai** — Redrob India Runs Data & AI Challenge

---

*TalentAI · Intelligent Candidate Discovery & Ranking*
