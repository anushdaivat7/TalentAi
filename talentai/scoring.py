"""Phase 4 & 5 - component scores and the final weighted ranking score.

Final score = base(5 components) * role_fit * trap_penalty, where:

    base = 0.40*skill + 0.25*experience + 0.15*project
         + 0.10*education + 0.10*behavioral

The weights are the challenge-specified scheme. On top of that we apply two
multipliers that encode the JD's "what it means, not what it says" intent:

    role_fit     - the decisive title/career-alignment signal
    trap_penalty - honeypot / keyword-stuffer / consulting / hopper modifiers

This hybrid (weighted components x semantic role-fit x behavioral/trap modifier)
is what separates real fits from keyword-stuffers and honeypots.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, Optional

from . import job_profile as jp
from .features import CandidateFeatures
from .traps import TrapReport, detect

# Component weights (challenge spec, Phase 5)
WEIGHTS = {
    "skill": 0.40,
    "experience": 0.25,
    "project": 0.15,
    "education": 0.10,
    "behavioral": 0.10,
}


@dataclass
class ScoreBreakdown:
    candidate_id: str
    final_score: float = 0.0           # 0..1
    skill_match: float = 0.0
    experience_match: float = 0.0
    project_relevance: float = 0.0
    education_match: float = 0.0
    behavioral: float = 0.0
    role_fit: float = 0.0
    semantic_similarity: float = 0.0
    trap_penalty: float = 1.0
    is_honeypot: bool = False
    components: Dict = field(default_factory=dict)


# --------------------------------------------------------------------------- #
# Individual component scores (each returns 0..1)                              #
# --------------------------------------------------------------------------- #
def skill_match_score(cf: CandidateFeatures, semantic: Optional[float]) -> float:
    """Weighted concept coverage, gated by skill trust, blended with semantics."""
    total_w = 0.0
    got_w = 0.0
    for concept in jp.REQUIRED_CONCEPTS + jp.PREFERRED_CONCEPTS:
        w = jp.CONCEPT_WEIGHTS.get(concept, 0.5)
        total_w += w
        if concept in cf.skill_concepts or concept in cf.career_concepts:
            # Career evidence counts a touch more than a bare skill tag.
            evidence = 1.0 if concept in cf.career_concepts else 0.85
            got_w += w * evidence
    coverage = (got_w / total_w) if total_w else 0.0

    # Trust gate: lists of skills with no endorsements/usage are discounted.
    trusted = coverage * (0.55 + 0.45 * cf.skill_trust)

    if semantic is not None:
        # Blend lexical concept coverage with dense semantic similarity.
        return min(1.0, 0.6 * trusted + 0.4 * semantic)
    return min(1.0, trusted)


def experience_match_score(cf: CandidateFeatures) -> float:
    """Gaussian-style fit around the ideal band + product-over-services bonus."""
    y = cf.years_experience
    e = jp.EXPERIENCE
    if e["ideal_low"] <= y <= e["ideal_high"]:
        band = 1.0
    elif e["min_years"] <= y <= e["max_years"]:
        band = 0.9
    else:
        # decay outside the 5-9 window
        if y < e["min_years"]:
            band = max(0.0, 1.0 - (e["min_years"] - y) / 4.0)
        else:
            band = max(0.0, 1.0 - (y - e["max_years"]) / 8.0)

    # Product-company share of career (services experience counts less).
    total = cf.product_company_months + cf.services_company_months
    product_share = (cf.product_company_months / total) if total else 0.4

    # Recent production coding matters for this IC role.
    coding = 1.0 if cf.recently_coding else 0.7

    score = 0.6 * band + 0.3 * product_share + 0.1 * coding
    return min(max(score, 0.0), 1.0)


def project_relevance_score(cf: CandidateFeatures, semantic: Optional[float]) -> float:
    """Did they actually build ranking/search/recsys/retrieval at a product co?"""
    high_value = {"ranking", "retrieval", "embeddings", "vector_db", "ml_evaluation"}
    hits = cf.career_concepts & high_value
    breadth = len(hits) / len(high_value)

    has_ml = 1.0 if (cf.career_concepts & {"ml_core", "nlp", "llm"}) else 0.0
    product = 1.0 if cf.product_company_months >= 12 else 0.4

    base = 0.55 * breadth + 0.25 * has_ml + 0.20 * product
    if semantic is not None:
        base = 0.7 * base + 0.3 * semantic
    return min(max(base, 0.0), 1.0)


def education_match_score(cf: CandidateFeatures) -> float:
    """Lightly weighted: tier + relevant field. JD welcomes plain-language fits."""
    tier_score = {"tier_1": 1.0, "tier_2": 0.8, "tier_3": 0.6, "tier_4": 0.45,
                  "unknown": 0.5}.get(cf.edu_best_tier, 0.5)
    field_score = 1.0 if cf.edu_relevant_field else 0.6
    return min(1.0, 0.6 * tier_score + 0.4 * field_score)


def role_fit_score(cf: CandidateFeatures, semantic: Optional[float]) -> float:
    """The decisive signal: does title + career actually match an AI eng role?

    This is what catches keyword stuffers (perfect skills, wrong job) and
    rewards plain-language Tier-5 fits (right job, modest keywords).
    """
    title_base = {"ai": 1.0, "adjacent": 0.7, "other": 0.45, "non_tech": 0.12}.get(
        cf.title_class, 0.4)

    evidence = 1.0 if cf.has_ai_career_evidence else 0.45
    fit = 0.6 * title_base + 0.4 * evidence

    if semantic is not None:
        fit = 0.7 * fit + 0.3 * semantic

    # An adjacent/other engineer with strong AI career evidence should not be
    # capped by their title alone.
    if cf.title_class in ("adjacent", "other") and cf.has_ai_career_evidence:
        fit = max(fit, 0.65)
    return min(max(fit, 0.05), 1.0)


# --------------------------------------------------------------------------- #
# Final score                                                                 #
# --------------------------------------------------------------------------- #
def score_candidate(
    cf: CandidateFeatures,
    semantic: Optional[float] = None,
    trap: Optional[TrapReport] = None,
) -> ScoreBreakdown:
    trap = trap or detect(cf)
    sb = ScoreBreakdown(candidate_id=cf.candidate_id)
    sb.semantic_similarity = float(semantic) if semantic is not None else 0.0
    sb.is_honeypot = trap.is_honeypot
    sb.trap_penalty = trap.penalty

    sb.skill_match = skill_match_score(cf, semantic)
    sb.experience_match = experience_match_score(cf)
    sb.project_relevance = project_relevance_score(cf, semantic)
    sb.education_match = education_match_score(cf)
    sb.behavioral = cf.behavior_score
    sb.role_fit = role_fit_score(cf, semantic)

    base = (
        WEIGHTS["skill"] * sb.skill_match +
        WEIGHTS["experience"] * sb.experience_match +
        WEIGHTS["project"] * sb.project_relevance +
        WEIGHTS["education"] * sb.education_match +
        WEIGHTS["behavioral"] * sb.behavioral
    )

    # role_fit and trap penalty are multiplicative modifiers on the weighted base.
    final = base * (0.35 + 0.65 * sb.role_fit) * trap.penalty

    # Round to 4 dp here so the ranking sort and the 4-dp CSV output agree on
    # ties (the validator requires candidate_id-ascending within equal scores).
    sb.final_score = round(min(max(final, 0.0), 1.0), 4)
    sb.components = {
        "skill_match": round(sb.skill_match, 4),
        "experience_match": round(sb.experience_match, 4),
        "project_relevance": round(sb.project_relevance, 4),
        "education_match": round(sb.education_match, 4),
        "behavioral": round(sb.behavioral, 4),
        "role_fit": round(sb.role_fit, 4),
        "semantic_similarity": round(sb.semantic_similarity, 4),
        "trap_penalty": round(sb.trap_penalty, 4),
        "base_weighted": round(base, 4),
    }
    return sb
