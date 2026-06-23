"""Trap detection: honeypots, keyword stuffers, behavioral twins.

The dataset contains ~80 honeypots with "subtly impossible" profiles that are
forced to relevance tier 0 in the ground truth. Ranking any in the top 100 hurts
us, and >10% in the top 100 is an automatic disqualification. We therefore push
detected honeypots to the very bottom of the ranking.

We also detect the softer traps the JD warns about (keyword stuffers, etc.) and
return penalty multipliers rather than hard rejection, because some of those
candidates are merely weak rather than fraudulent.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Dict, List

from .features import CandidateFeatures, _parse_date


@dataclass
class TrapReport:
    is_honeypot: bool = False
    honeypot_reasons: List[str] = field(default_factory=list)
    penalty: float = 1.0  # multiplicative (1.0 = no penalty, 0.0 = killed)
    penalty_reasons: List[str] = field(default_factory=list)


def detect(cf: CandidateFeatures) -> TrapReport:
    rep = TrapReport()
    rec = cf.raw
    career = rec.get("career_history", []) or []
    skills = rec.get("skills", []) or []
    education = rec.get("education", []) or []

    # ------------------------------------------------------------------ #
    # 1. HONEYPOTS - subtly impossible profiles -> forced to the bottom  #
    # ------------------------------------------------------------------ #
    # (a) expert/advanced proficiency with 0 months of usage (multiple)
    impossible_skills = sum(
        1 for s in skills
        if (s.get("proficiency") in ("advanced", "expert")) and (s.get("duration_months", 0) or 0) == 0
    )
    if impossible_skills >= 3:
        rep.honeypot_reasons.append(
            f"{impossible_skills} skills claimed advanced/expert with 0 months of use"
        )

    # (b) career duration inconsistent with stated start/end dates
    date_mismatch = 0
    bad_order = 0
    for job in career:
        sd = _parse_date(job.get("start_date"))
        ed = _parse_date(job.get("end_date")) or date(2026, 6, 1)
        dur = int(job.get("duration_months", 0) or 0)
        if sd and ed:
            if ed < sd:
                bad_order += 1
            months = (ed.year - sd.year) * 12 + (ed.month - sd.month)
            if dur - months > 9:  # claims materially more time than dates allow
                date_mismatch += 1
    if bad_order:
        rep.honeypot_reasons.append(f"{bad_order} job(s) with end date before start date")
    if date_mismatch:
        rep.honeypot_reasons.append(
            f"{date_mismatch} job(s) whose duration exceeds the start/end window"
        )

    # (c) total career tenure wildly exceeds stated years of experience
    total_months = sum(int(j.get("duration_months", 0) or 0) for j in career)
    yoe_months = cf.years_experience * 12.0
    if yoe_months > 0 and total_months - yoe_months > 60:
        rep.honeypot_reasons.append(
            "summed job tenure far exceeds stated years of experience"
        )

    # (d) tenure at a single company longer than the candidate's whole career
    if career:
        longest = max(int(j.get("duration_months", 0) or 0) for j in career)
        if yoe_months > 0 and longest > yoe_months + 18:
            rep.honeypot_reasons.append(
                "tenure at one company exceeds total years of experience"
            )

    # (e) impossible education timeline
    for e in education:
        sy, ey = e.get("start_year"), e.get("end_year")
        if isinstance(sy, int) and isinstance(ey, int) and ey < sy:
            rep.honeypot_reasons.append("education end year precedes start year")
            break

    if rep.honeypot_reasons:
        rep.is_honeypot = True
        rep.penalty = 0.0
        return rep  # no need to compute soft penalties; it's dead last

    # ------------------------------------------------------------------ #
    # 2. SOFT TRAPS - multiplicative penalties                          #
    # ------------------------------------------------------------------ #
    penalty = 1.0

    # Keyword stuffer: non-technical title, many AI skills, no career evidence.
    ai_skill_count = len(cf.required_concepts_hit) + len(cf.preferred_concepts_hit)
    if cf.title_class == "non_tech" and ai_skill_count >= 3 and not cf.has_ai_career_evidence:
        penalty *= 0.18
        rep.penalty_reasons.append(
            f"keyword stuffer: '{cf.current_title}' lists AI skills with no career evidence"
        )
    elif cf.title_class == "non_tech" and not cf.has_ai_career_evidence:
        penalty *= 0.35
        rep.penalty_reasons.append("non-technical role with no AI/ML career evidence")

    # Suspicious skill stuffing (advanced/expert, 0 months) below honeypot bar.
    if cf.suspicious_skills >= 1:
        penalty *= max(0.6, 1.0 - 0.15 * cf.suspicious_skills)
        rep.penalty_reasons.append(
            f"{cf.suspicious_skills} skill(s) claimed advanced/expert with no usage history"
        )

    # Consulting-only career.
    if cf.is_consulting_only:
        penalty *= 0.45
        rep.penalty_reasons.append("entire career at IT-services/consulting firms")

    # Title-chaser / job-hopper.
    if cf.is_job_hopper:
        penalty *= 0.6
        rep.penalty_reasons.append(
            f"job-hopper pattern (avg tenure {cf.avg_tenure_months:.0f} months)"
        )

    # Research-only, no production.
    if cf.is_research_only:
        penalty *= 0.55
        rep.penalty_reasons.append("research-only background with no production deployment")

    # CV/speech/robotics dominant without NLP/IR.
    if cf.cv_speech_robotics_skills >= 3 and "nlp" not in cf.skill_concepts \
            and "retrieval" not in cf.skill_concepts:
        penalty *= 0.6
        rep.penalty_reasons.append("computer-vision/speech/robotics focus without NLP/IR")

    # Stale / unavailable (down-weight, do not kill).
    if cf.days_since_active > 180 and cf.recruiter_response_rate < 0.15:
        penalty *= 0.7
        rep.penalty_reasons.append("inactive and low recruiter response rate (low availability)")

    rep.penalty = max(penalty, 0.02)
    return rep
