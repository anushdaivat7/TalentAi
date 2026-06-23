"""TalentAI - Intelligent Candidate Discovery & Ranking System.

Core library powering the Redrob "India Runs Data & AI Challenge" submission.

Modules:
    paths            - locate challenge data files
    data             - stream/load candidate records (jsonl / jsonl.gz)
    schema_validation- validate candidate records against candidate_schema.json
    job_profile      - structured Senior AI Engineer job profile + skill ontology
    features         - extract normalized features from a raw candidate record
    traps            - honeypot / keyword-stuffer / consulting / job-hopper detection
    scoring          - the five component scores + weighted final score
    embeddings       - sentence-transformers (all-MiniLM-L6-v2) wrapper (offline)
    faiss_index      - FAISS vector index build/search (offline)
    explain          - rule-based strengths / weaknesses / reasoning
    gemini           - optional Gemini explanation layer (offline only)
    ranker           - orchestrates the full ranking pipeline
    submission       - write a spec-compliant submission CSV
"""

__version__ = "1.0.0"
