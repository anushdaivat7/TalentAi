"""Phase 7 - dashboard cards + charts."""
from __future__ import annotations

from fastapi import APIRouter

from ..services import analytics
from ..store import store

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary():
    return analytics.summary_cards(store.ranked)


@router.get("/charts")
def charts():
    r = store.ranked
    return {
        "ranking_distribution": analytics.ranking_distribution(r),
        "skill_distribution": analytics.skill_distribution(r),
        "experience_distribution": analytics.experience_distribution(r),
        "education_distribution": analytics.education_distribution(r),
        "score_breakdown": analytics.score_breakdown(r, top_n=10),
    }


@router.get("/score-breakdown")
def score_breakdown(top_n: int = 10):
    return analytics.score_breakdown(store.ranked, top_n=top_n)


@router.get("/trap-stats")
def trap_stats():
    stats = dict(store.trap_stats or {})
    # Fallback if the pool-wide file isn't present yet: derive from top-100.
    if not stats:
        ranked = store.ranked
        stats = {
            "total_scanned": None,
            "honeypots_detected": None,
            "honeypots_in_top": sum(1 for r in ranked if r.get("is_honeypot")),
            "top_k": len(ranked),
            "soft_trap_categories": [],
        }
    return stats


@router.get("/job-profile")
def job_profile():
    return store.job_profile
