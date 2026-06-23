"""Helpers to build valid candidate records for tests (schema-compliant)."""
from __future__ import annotations

import copy
from typing import Dict, List, Optional

_BASE: Dict = {
    "candidate_id": "CAND_0000001",
    "profile": {
        "anonymized_name": "Test Person",
        "headline": "Senior AI Engineer | Retrieval, Ranking",
        "summary": "Built embeddings-based retrieval and ranking systems at a product company.",
        "location": "Pune",
        "country": "India",
        "years_of_experience": 7.0,
        "current_title": "Senior AI Engineer",
        "current_company": "ProductCo",
        "current_company_size": "201-500",
        "current_industry": "Software",
    },
    "career_history": [
        {
            "company": "ProductCo",
            "title": "Senior AI Engineer",
            "start_date": "2021-01-01",
            "end_date": None,
            "duration_months": 60,
            "is_current": True,
            "industry": "Software",
            "company_size": "201-500",
            "description": "Built semantic search, embeddings retrieval and a recommendation "
                           "ranking system with NDCG/MRR evaluation in production.",
        }
    ],
    "education": [
        {
            "institution": "IIT",
            "degree": "B.Tech",
            "field_of_study": "Computer Science",
            "start_year": 2012,
            "end_year": 2016,
            "grade": "8.5 CGPA",
            "tier": "tier_1",
        }
    ],
    "skills": [
        {"name": "Embeddings", "proficiency": "expert", "endorsements": 30, "duration_months": 48},
        {"name": "FAISS", "proficiency": "advanced", "endorsements": 20, "duration_months": 36},
        {"name": "Retrieval", "proficiency": "advanced", "endorsements": 25, "duration_months": 40},
        {"name": "Python", "proficiency": "expert", "endorsements": 40, "duration_months": 84},
    ],
    "certifications": [],
    "languages": [],
    "redrob_signals": {
        "profile_completeness_score": 90,
        "signup_date": "2023-01-01",
        "last_active_date": "2026-05-20",
        "open_to_work_flag": True,
        "profile_views_received_30d": 50,
        "applications_submitted_30d": 3,
        "recruiter_response_rate": 0.8,
        "avg_response_time_hours": 5,
        "skill_assessment_scores": {},
        "connection_count": 300,
        "endorsements_received": 100,
        "notice_period_days": 30,
        "expected_salary_range_inr_lpa": {"min": 30, "max": 45},
        "preferred_work_mode": "hybrid",
        "willing_to_relocate": True,
        "github_activity_score": 70,
        "search_appearance_30d": 40,
        "saved_by_recruiters_30d": 5,
        "interview_completion_rate": 0.9,
        "offer_acceptance_rate": 0.5,
        "verified_email": True,
        "verified_phone": True,
        "linkedin_connected": True,
    },
}


def make_candidate(cid: str = "CAND_0000001", **overrides) -> Dict:
    """Deep-copy the base record and apply nested overrides.

    Nested keys can be overridden via dot paths, e.g.
        make_candidate(**{"profile.current_title": "Marketing Manager"})
    or by passing whole sub-dicts via `profile=`, `skills=`, etc.
    """
    rec = copy.deepcopy(_BASE)
    rec["candidate_id"] = cid
    for key, value in overrides.items():
        if "." in key:
            parts = key.split(".")
            node = rec
            for p in parts[:-1]:
                node = node[p]
            node[parts[-1]] = value
        else:
            rec[key] = value
    return rec
