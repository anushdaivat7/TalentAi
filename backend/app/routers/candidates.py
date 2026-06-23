"""Phase 7 - candidate listing, detail and search."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..store import store

router = APIRouter(prefix="/api/candidates", tags=["candidates"])


@router.get("")
def list_candidates(
    q: Optional[str] = Query(None, description="free text: name/title/id/skill"),
    skill: Optional[str] = None,
    min_experience: Optional[float] = None,
    max_experience: Optional[float] = None,
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
    trap: Optional[str] = None,
    hide_honeypots: bool = False,
    sort: str = "rank",
    limit: int = 100,
    offset: int = 0,
):
    rows = store.ranked

    def matches(r):
        if hide_honeypots and r.get("is_honeypot"):
            return False
        if q:
            blob = " ".join(str(r.get(k, "")) for k in
                            ["candidate_id", "name", "current_title", "current_company",
                             "location", "explanation"]).lower()
            blob += " ".join(r.get("matching_skills", [])).lower()
            if q.lower() not in blob:
                return False
        if skill:
            if not any(skill.lower() in s.lower() for s in r.get("matching_skills", [])):
                return False
        if trap:
            blob = " ".join(r.get("weaknesses", [])).lower()
            if trap.lower() not in blob:
                return False
        y = r.get("years_experience")
        if min_experience is not None and (y is None or y < min_experience):
            return False
        if max_experience is not None and (y is None or y > max_experience):
            return False
        s = r.get("final_score", 0)
        if min_score is not None and s < min_score:
            return False
        if max_score is not None and s > max_score:
            return False
        return True

    filtered = [r for r in rows if matches(r)]

    reverse = sort in ("score", "experience")
    keymap = {
        "rank": lambda r: r.get("rank", 9999),
        "score": lambda r: r.get("final_score", 0),
        "experience": lambda r: r.get("years_experience") or 0,
    }
    filtered.sort(key=keymap.get(sort, keymap["rank"]), reverse=reverse)

    total = len(filtered)
    page = filtered[offset:offset + limit]
    return {"total": total, "count": len(page), "results": page}


@router.get("/{candidate_id}")
def candidate_detail(candidate_id: str):
    r = store.by_id.get(candidate_id)
    if not r:
        raise HTTPException(status_code=404, detail="candidate not found in ranking")
    raw = store.raw_candidate(candidate_id)
    return {"ranking": r, "raw": raw}
