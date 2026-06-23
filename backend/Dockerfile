# TalentAI backend (FastAPI). Build context = repo root so the `talentai`
# package is available to the API for on-the-fly ranking / submission gen.
FROM python:3.11-slim

WORKDIR /app

# System deps kept minimal; faiss-cpu/sentence-transformers wheels are prebuilt.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./root-requirements.txt
COPY backend/requirements.txt ./backend-requirements.txt
RUN pip install --no-cache-dir -r backend-requirements.txt

# App code
COPY talentai ./talentai
COPY backend ./backend
COPY results ./results
COPY artifacts ./artifacts

ENV PYTHONUNBUFFERED=1
WORKDIR /app/backend
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
