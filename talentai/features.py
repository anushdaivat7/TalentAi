"""Phase 3 - extract normalized, machine-usable features from a raw candidate.

This is the "candidate understanding" layer. Every downstream component
(scoring, trap detection, explanation) consumes `CandidateFeatures`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Dict, List, Optional, Set

from . import job_profile as jp

# Reference "today" for recency math. Using a fixed anchor keeps ranking
# deterministic and reproducible (a hard requirement at Stage 3).
REFERENCE_DATE = date(2026, 6, 1)


def _parse_date(s: Optional[str]) -> Optional[date]:
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%Y-%m", "%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def _norm(s: Optional[str]) -> str:
    return (s or "").strip().lower()


def _concepts_in_text(text: str) -> Set[str]:
    """Return the set of ontology concepts whose surface forms appear in text."""
    t = " " + text.lower() + " "
    found: Set[str] = set()
    for concept, forms in jp.SKILL_ONTOLOGY.items():
        for form in forms:
            if form in t:
                found.add(concept)
                break
    return found


@dataclass
class CandidateFeatures:
    candidate_id: str
    name: str
    headline: str
    summary: str
    current_title: str
    current_company: str
    current_industry: str
    location: str
    country: str
    years_experience: float

    # Skills
    skill_names: List[str] = field(default_factory=list)
    skill_concepts: Set[str] = field(default_factory=set)
    required_concepts_hit: Set[str] = field(default_factory=set)
    preferred_concepts_hit: Set[str] = field(default_factory=set)
    missing_required: Set[str] = field(default_factory=set)
    cv_speech_robotics_skills: int = 0
    skill_trust: float = 0.0          # 0..1 - endorsement+duration backed depth
    suspicious_skills: int = 0        # advanced/expert with 0 months used

    # Career
    n_jobs: int = 0
    avg_tenure_months: float = 0.0
    product_company_months: float = 0.0
    services_company_months: float = 0.0
    career_concepts: Set[str] = field(default_factory=set)
    has_ai_career_evidence: bool = False
    is_consulting_only: bool = False
    is_job_hopper: bool = False
    is_research_only: bool = False
    recently_coding: bool = True

    # Title
    title_class: str = "other"        # ai | adjacent | non_tech | other

    # Education
    edu_best_tier: str = "unknown"
    edu_relevant_field: bool = False
    edu_degrees: List[str] = field(default_factory=list)

    # Location
    location_fit: float = 0.0         # 0..1

    # Behavioral
    behavior_score: float = 0.0       # 0..1
    days_since_active: int = 9999
    recruiter_response_rate: float = 0.0
    open_to_work: bool = False
    github_activity: float = -1.0
    willing_to_relocate: bool = False
    notice_period_days: int = 0

    # Text for embeddings
    embedding_text: str = ""

    # Raw passthrough (for the dashboard / explainer)
    raw: Dict = field(default_factory=dict)


def _title_class(title: str) -> str:
    t = _norm(title)
    for term in jp.AI_TITLE_TERMS:
        if term in t:
            return "ai"
    for term in jp.NON_TECH_TITLE_TERMS:
        if term in t:
            return "non_tech"
    for term in jp.ADJACENT_TECH_TITLE_TERMS:
        if term in t:
            return "adjacent"
    return "other"


def _skill_trust(skills: List[Dict]) -> tuple[float, int]:
    """Trust = depth backed by endorsements + months used. Penalizes stuffing."""
    if not skills:
        return 0.0, 0
    prof_w = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.85, "expert": 1.0}
    total = 0.0
    suspicious = 0
    for s in skills:
        prof = _norm(s.get("proficiency"))
        dur = s.get("duration_months", 0) or 0
        end = s.get("endorsements", 0) or 0
        if prof in ("advanced", "expert") and dur == 0:
            suspicious += 1
        # A skill is "trusted" when it has real months + some endorsements.
        depth = min(dur / 24.0, 1.0) * 0.6 + min(end / 30.0, 1.0) * 0.4
        total += prof_w.get(prof, 0.4) * depth
    avg = total / len(skills)
    return min(avg, 1.0), suspicious


def extract_features(rec: Dict) -> CandidateFeatures:
    profile = rec.get("profile", {}) or {}
    skills = rec.get("skills", []) or []
    career = rec.get("career_history", []) or []
    education = rec.get("education", []) or []
    signals = rec.get("redrob_signals", {}) or {}

    cid = rec.get("candidate_id", "")
    cf = CandidateFeatures(
        candidate_id=cid,
        name=profile.get("anonymized_name", ""),
        headline=profile.get("headline", ""),
        summary=profile.get("summary", ""),
        current_title=profile.get("current_title", ""),
        current_company=profile.get("current_company", ""),
        current_industry=profile.get("current_industry", ""),
        location=profile.get("location", ""),
        country=profile.get("country", ""),
        years_experience=float(profile.get("years_of_experience", 0) or 0),
        raw=rec,
    )

    # ---- Skills -------------------------------------------------------- #
    cf.skill_names = [s.get("name", "") for s in skills]
    skills_text = " ".join(cf.skill_names)
    cf.skill_concepts = _concepts_in_text(skills_text)
    cf.required_concepts_hit = cf.skill_concepts & set(jp.REQUIRED_CONCEPTS)
    cf.preferred_concepts_hit = cf.skill_concepts & set(jp.PREFERRED_CONCEPTS)
    cf.missing_required = set(jp.REQUIRED_CONCEPTS) - cf.skill_concepts
    cv_terms = jp.SKILL_ONTOLOGY["cv_speech_robotics"]
    cf.cv_speech_robotics_skills = sum(
        1 for n in cf.skill_names if any(term in _norm(n) for term in cv_terms)
    )
    cf.skill_trust, cf.suspicious_skills = _skill_trust(skills)

    # ---- Title --------------------------------------------------------- #
    cf.title_class = _title_class(cf.current_title)

    # ---- Career history ------------------------------------------------ #
    cf.n_jobs = len(career)
    tenures: List[int] = []
    product_months = 0.0
    services_months = 0.0
    career_text_parts: List[str] = []
    consulting_hits = 0
    research_hits = 0
    for job in career:
        dur = int(job.get("duration_months", 0) or 0)
        tenures.append(dur)
        company = _norm(job.get("company"))
        industry = _norm(job.get("industry"))
        title = _norm(job.get("title"))
        desc = job.get("description", "") or ""
        career_text_parts.append(f"{title} {company} {industry} {desc}")

        is_consult = any(firm == company or firm in company for firm in jp.CONSULTING_FIRMS) \
            or "it services" in industry or "consulting" in industry
        if is_consult:
            consulting_hits += 1
            services_months += dur
        else:
            product_months += dur

        if any(term in title for term in jp.RESEARCH_TERMS) or \
           any(ind in industry for ind in jp.RESEARCH_INDUSTRIES):
            research_hits += 1

    cf.avg_tenure_months = (sum(tenures) / len(tenures)) if tenures else 0.0
    cf.product_company_months = product_months
    cf.services_company_months = services_months
    career_text = " ".join(career_text_parts)
    cf.career_concepts = _concepts_in_text(career_text)
    ai_concepts = {"embeddings", "retrieval", "vector_db", "ranking", "nlp", "ml_core", "llm"}
    cf.has_ai_career_evidence = bool(cf.career_concepts & ai_concepts)

    cf.is_consulting_only = cf.n_jobs > 0 and consulting_hits == cf.n_jobs
    # job-hopper: 3+ jobs and average tenure < 18 months
    cf.is_job_hopper = cf.n_jobs >= 3 and cf.avg_tenure_months < 18.0
    cf.is_research_only = cf.n_jobs > 0 and research_hits == cf.n_jobs and not cf.has_ai_career_evidence

    # recently coding: current/most-recent role is an engineering IC role
    if career:
        latest = sorted(career, key=lambda j: j.get("start_date", ""), reverse=True)[0]
        latest_title = _norm(latest.get("title"))
        mgmt = any(t in latest_title for t in ["manager", "director", "vp", "head", "lead"])
        cf.recently_coding = not mgmt or "engineer" in latest_title

    # ---- Education ----------------------------------------------------- #
    tier_rank = {"tier_1": 4, "tier_2": 3, "tier_3": 2, "tier_4": 1, "unknown": 0}
    best = "unknown"
    rel = False
    for e in education:
        tier = _norm(e.get("tier")) or "unknown"
        if tier_rank.get(tier, 0) > tier_rank.get(best, 0):
            best = tier
        field_s = _norm(e.get("field_of_study"))
        if any(k in field_s for k in ["computer", "data", "machine learning", "artificial",
                                       "statistics", "math", "electronics", "information"]):
            rel = True
        cf.edu_degrees.append(e.get("degree", ""))
    cf.edu_best_tier = best
    cf.edu_relevant_field = rel

    # ---- Location ------------------------------------------------------ #
    loc = _norm(cf.location)
    country = _norm(cf.country)
    relocate = bool(signals.get("willing_to_relocate", False))
    if any(city in loc for city in jp.PREFERRED_LOCATIONS):
        cf.location_fit = 1.0
    elif country == jp.PREFERRED_COUNTRY:
        cf.location_fit = 0.75 if relocate else 0.6
    elif relocate:
        cf.location_fit = 0.5
    else:
        cf.location_fit = 0.2
    cf.willing_to_relocate = relocate

    # ---- Behavioral signals ------------------------------------------- #
    last_active = _parse_date(signals.get("last_active_date"))
    cf.days_since_active = (REFERENCE_DATE - last_active).days if last_active else 9999
    cf.recruiter_response_rate = float(signals.get("recruiter_response_rate", 0) or 0)
    cf.open_to_work = bool(signals.get("open_to_work_flag", False))
    cf.github_activity = float(signals.get("github_activity_score", -1) or -1)
    cf.notice_period_days = int(signals.get("notice_period_days", 0) or 0)
    cf.behavior_score = _behavior_score(cf, signals)

    # ---- Embedding text ------------------------------------------------ #
    cf.embedding_text = " . ".join(filter(None, [
        cf.headline, cf.summary, f"Current role: {cf.current_title} at {cf.current_company}",
        "Skills: " + ", ".join(cf.skill_names),
        "Experience: " + career_text[:1500],
    ]))

    return cf


def _behavior_score(cf: CandidateFeatures, signals: Dict) -> float:
    """Composite availability/engagement score in 0..1 (Phase 4 component)."""
    # Recency: full credit if active within 30 days, decays to ~0 by ~270 days.
    if cf.days_since_active <= 30:
        recency = 1.0
    elif cf.days_since_active >= 270:
        recency = 0.0
    else:
        recency = max(0.0, 1.0 - (cf.days_since_active - 30) / 240.0)

    response = min(max(cf.recruiter_response_rate, 0.0), 1.0)
    interview = float(signals.get("interview_completion_rate", 0) or 0)
    completeness = float(signals.get("profile_completeness_score", 0) or 0) / 100.0
    saved = min((signals.get("saved_by_recruiters_30d", 0) or 0) / 10.0, 1.0)
    gh = (cf.github_activity / 100.0) if cf.github_activity >= 0 else 0.3  # neutral if no GitHub
    open_flag = 1.0 if cf.open_to_work else 0.4

    score = (
        0.30 * response +
        0.22 * recency +
        0.15 * open_flag +
        0.12 * interview +
        0.10 * completeness +
        0.06 * saved +
        0.05 * gh
    )
    return min(max(score, 0.0), 1.0)
