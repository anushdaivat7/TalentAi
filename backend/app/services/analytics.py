"""Dashboard analytics derived from the ranked candidate list."""
from __future__ import annotations

from collections import Counter
from typing import Dict, List


def _exp_bucket(years_text) -> str:
    return years_text


def summary_cards(ranked: List[Dict]) -> Dict:
    if not ranked:
        return {"total_candidates": 0, "avg_match_score": 0,
                "top_candidate": None, "total_skills_matched": 0}

    scores = [r["final_score"] for r in ranked]
    total_skills = sum(len(r.get("matching_skills", [])) for r in ranked)
    top = ranked[0]
    return {
        "total_candidates": len(ranked),
        "avg_match_score": round(sum(scores) / len(scores), 1),
        "top_candidate": {
            "candidate_id": top["candidate_id"],
            "score": top["final_score"],
            "explanation": top.get("explanation", ""),
        },
        "total_skills_matched": total_skills,
        "honeypots_in_top100": sum(1 for r in ranked if r.get("is_honeypot")),
    }


def ranking_distribution(ranked: List[Dict]) -> List[Dict]:
    """Histogram of scores in 10-point buckets (0-100)."""
    buckets = Counter()
    for r in ranked:
        b = min(int(r["final_score"] // 10) * 10, 90)
        buckets[b] += 1
    return [{"range": f"{b}-{b + 10}", "count": buckets.get(b, 0)} for b in range(0, 100, 10)]


def skill_distribution(ranked: List[Dict], top_n: int = 12) -> List[Dict]:
    c = Counter()
    for r in ranked:
        for s in r.get("matching_skills", []):
            c[s] += 1
    return [{"skill": k, "count": v} for k, v in c.most_common(top_n)]


def experience_distribution(ranked: List[Dict]) -> List[Dict]:
    """Buckets derived from the years mentioned in each candidate's components."""
    buckets = Counter()
    order = ["0-3", "3-5", "5-7", "7-9", "9-12", "12+"]
    for r in ranked:
        y = _years_from(r)
        if y is None:
            continue
        if y < 3:
            k = "0-3"
        elif y < 5:
            k = "3-5"
        elif y < 7:
            k = "5-7"
        elif y < 9:
            k = "7-9"
        elif y < 12:
            k = "9-12"
        else:
            k = "12+"
        buckets[k] += 1
    return [{"range": k, "count": buckets.get(k, 0)} for k in order]


def education_distribution(ranked: List[Dict]) -> List[Dict]:
    """Tier mix where available (from raw component metadata)."""
    c = Counter()
    for r in ranked:
        tier = (r.get("education_tier") or "unknown")
        c[tier] += 1
    order = ["tier_1", "tier_2", "tier_3", "tier_4", "unknown"]
    return [{"tier": t, "count": c.get(t, 0)} for t in order if c.get(t, 0) or t in order]


_WEIGHTS = {"skill_match": 40, "experience_match": 25, "project_relevance": 15,
            "education_match": 10, "behavioral": 10}


def score_breakdown(ranked: List[Dict], top_n: int = 10) -> List[Dict]:
    """Per-candidate weighted contribution of each component (points out of 100).

    The five stacked values sum to the candidate's *base* score; the final score
    additionally reflects the role-fit and trap multipliers (shown separately).
    """
    out = []
    for r in ranked[:top_n]:
        comp = r.get("components", {}) or {}
        row = {
            "candidate_id": r["candidate_id"],
            "rank": r.get("rank"),
            "final_score": r.get("final_score"),
            "role_fit": round((comp.get("role_fit", 0) or 0) * 100, 1),
            "trap_penalty": round((comp.get("trap_penalty", 1) or 1) * 100, 1),
        }
        for key, w in _WEIGHTS.items():
            label = {
                "skill_match": "Skill",
                "experience_match": "Experience",
                "project_relevance": "Project",
                "education_match": "Education",
                "behavioral": "Behavioral",
            }[key]
            row[label] = round((comp.get(key, 0) or 0) * w, 2)
        out.append(row)
    return out


def _years_from(r: Dict):
    """Years of experience, preferring the structured field, else the reasoning."""
    if r.get("years_experience") is not None:
        try:
            return float(r["years_experience"])
        except (ValueError, TypeError):
            pass
    import re

    m = re.search(r"([0-9]+\.[0-9])\s*yrs", r.get("explanation", ""))
    if m:
        try:
            return float(m.group(1))
        except ValueError:
            return None
    return None
