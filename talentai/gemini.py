"""Optional Gemini explanation layer (DASHBOARD ONLY - never during ranking).

The submission ranking step must run with the network OFF, so Gemini is *never*
called there. This module is used only to enrich explanations for the recruiter
dashboard and chatbot, where network access is allowed. It degrades gracefully:
if no GEMINI_API_KEY is set or the package is missing, callers fall back to the
grounded rule-based explanations from explain.py.
"""
from __future__ import annotations

import json
import os
from functools import lru_cache
from typing import Dict, List, Optional

MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def available() -> bool:
    return bool(os.getenv("GEMINI_API_KEY"))


@lru_cache(maxsize=1)
def _client():
    if not available():
        return None
    try:
        import google.generativeai as genai  # lazy import

        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        return genai.GenerativeModel(MODEL)
    except Exception:
        return None


def _generate(prompt: str) -> Optional[str]:
    model = _client()
    if model is None:
        return None
    try:
        resp = model.generate_content(prompt)
        return (resp.text or "").strip()
    except Exception:
        return None


def enrich_explanation(candidate_explanation: Dict, job_summary: str) -> str:
    """Rewrite a grounded explanation into recruiter-friendly prose.

    Falls back to the rule-based explanation if Gemini is unavailable.
    """
    fallback = candidate_explanation.get("explanation", "")
    prompt = f"""You are a senior technical recruiter. Using ONLY the facts below,
write a concise 2-3 sentence justification for this candidate's ranking. Do not
invent skills or experience. Acknowledge real gaps honestly.

JOB: {job_summary}

CANDIDATE FACTS (JSON):
{json.dumps({k: candidate_explanation.get(k) for k in
             ['final_score', 'strengths', 'weaknesses', 'matching_skills', 'missing_skills']},
            ensure_ascii=False)}

Justification:"""
    return _generate(prompt) or fallback


def answer_question(question: str, context: Dict) -> Optional[str]:
    """Used by the chatbot to produce natural-language answers over ranking data."""
    prompt = f"""You are an AI recruiting assistant for the role below. Answer the
recruiter's question using ONLY the provided ranking context. Be specific, cite
candidate IDs and facts, and keep it concise.

ROLE: {context.get('job_summary', '')}

RANKING CONTEXT (JSON):
{json.dumps(context.get('data', {}), ensure_ascii=False)[:6000]}

QUESTION: {question}

Answer:"""
    return _generate(prompt)
