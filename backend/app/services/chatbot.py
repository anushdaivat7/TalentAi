"""Phase 8 - AI recruiter chatbot.

Answers recruiter questions over the ranked-candidate data. Uses Gemini when
GEMINI_API_KEY is configured (richer prose); otherwise it falls back to robust
rule-based answers so the chatbot always works offline.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Dict, List

from .. import store as store_mod


def answer(question: str) -> Dict:
    ranked = store_mod.store.ranked
    job = store_mod.store.job_profile
    if not ranked:
        return {"answer": "No ranking is loaded yet. Run the ranking pipeline first.",
                "source": "system", "candidates": []}

    q = question.lower().strip()

    # Rule-based intent routing (deterministic, fast, offline).
    rule = _route(q, ranked)

    # Optionally upgrade with Gemini natural language.
    try:
        from talentai import gemini

        if gemini.available():
            ctx = {
                "job_summary": job.get("summary_text", "Senior AI Engineer at Redrob AI"),
                "data": rule.get("context", {}),
            }
            text = gemini.answer_question(question, ctx)
            if text:
                return {"answer": text, "source": "gemini",
                        "candidates": rule.get("candidates", [])}
    except Exception:
        pass

    return {"answer": rule["answer"], "source": "rules",
            "candidates": rule.get("candidates", [])}


def _card(r: Dict) -> Dict:
    return {
        "candidate_id": r["candidate_id"],
        "rank": r.get("rank"),
        "score": r.get("final_score"),
        "title": r.get("current_title"),
        "explanation": r.get("explanation"),
    }


def _route(q: str, ranked: List[Dict]) -> Dict:
    # "why is candidate X ranked first" / "why is CAND_xxxx ranked ..."
    m = re.search(r"cand[_ ]?(\d{6,7})", q)
    if "why" in q and (m or "first" in q or "top" in q or "rank" in q):
        target = ranked[0]
        if m:
            cid = "CAND_" + m.group(1).zfill(7)
            target = next((r for r in ranked if r["candidate_id"] == cid), ranked[0])
        strengths = "; ".join(target.get("strengths", [])[:4])
        weak = "; ".join(target.get("weaknesses", [])[:3]) or "no major concerns"
        ans = (f"{target['candidate_id']} is ranked #{target.get('rank')} "
               f"(score {target.get('final_score')}). "
               f"{target.get('explanation')} Strengths: {strengths}. Concerns: {weak}.")
        return {"answer": ans, "candidates": [_card(target)],
                "context": {"candidate": target}}

    # "show top N candidates"
    m = re.search(r"top\s+(\d+)", q)
    if "top" in q or "show" in q or "list" in q:
        n = int(m.group(1)) if m else 10
        n = max(1, min(n, len(ranked)))
        rows = ranked[:n]
        lines = [f"#{r['rank']} {r['candidate_id']} ({r.get('current_title')}, "
                 f"score {r['final_score']})" for r in rows]
        return {"answer": f"Top {n} candidates:\n" + "\n".join(lines),
                "candidates": [_card(r) for r in rows],
                "context": {"top": [_card(r) for r in rows]}}

    # "which skills are most missing"
    if "missing" in q and "skill" in q:
        c = Counter()
        for r in ranked:
            for s in r.get("missing_skills", []):
                c[s] += 1
        top = c.most_common(8)
        ans = "Most commonly missing skills across the top candidates:\n" + \
              "\n".join(f"- {k} (missing in {v})" for k, v in top)
        return {"answer": ans, "candidates": [],
                "context": {"missing_skills": top}}

    # "recommend interview shortlist"
    if "shortlist" in q or "interview" in q:
        shortlist = [r for r in ranked
                     if not r.get("is_honeypot") and r.get("final_score", 0) >= 75][:10]
        if not shortlist:
            shortlist = ranked[:8]
        lines = [f"#{r['rank']} {r['candidate_id']} - {r.get('current_title')} "
                 f"({r['final_score']}): {r.get('explanation')[:120]}" for r in shortlist]
        return {"answer": "Recommended interview shortlist:\n" + "\n".join(lines),
                "candidates": [_card(r) for r in shortlist],
                "context": {"shortlist": [_card(r) for r in shortlist]}}

    # "strongest for this role"
    if "strong" in q or "best" in q:
        rows = ranked[:5]
        lines = [f"#{r['rank']} {r['candidate_id']} ({r.get('current_title')}): "
                 f"{r.get('explanation')}" for r in rows]
        return {"answer": "Strongest candidates for this role:\n" + "\n".join(lines),
                "candidates": [_card(r) for r in rows],
                "context": {"top": [_card(r) for r in rows]}}

    # default: top 5
    rows = ranked[:5]
    return {"answer": ("I can answer things like: 'Why is candidate X ranked first?', "
                       "'Show top 10 candidates', 'Which skills are most missing?', "
                       "'Recommend an interview shortlist'.\n\nHere are the current top 5:\n" +
                       "\n".join(f"#{r['rank']} {r['candidate_id']} ({r['final_score']})"
                                 for r in rows)),
            "candidates": [_card(r) for r in rows],
            "context": {"top": [_card(r) for r in rows]}}
