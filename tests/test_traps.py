"""Trap-detection tests: honeypots and soft-penalty traps."""
from talentai.features import extract_features
from talentai.traps import detect
from tests.factory import make_candidate


def _report(rec):
    return detect(extract_features(rec))


def test_clean_candidate_is_not_a_honeypot():
    rep = _report(make_candidate())
    assert rep.is_honeypot is False
    assert rep.penalty == 1.0


def test_honeypot_expert_skills_with_zero_months():
    rec = make_candidate(skills=[
        {"name": "Embeddings", "proficiency": "expert", "endorsements": 0, "duration_months": 0},
        {"name": "FAISS", "proficiency": "expert", "endorsements": 0, "duration_months": 0},
        {"name": "Retrieval", "proficiency": "advanced", "endorsements": 0, "duration_months": 0},
    ])
    rep = _report(rec)
    assert rep.is_honeypot is True
    assert rep.penalty == 0.0


def test_honeypot_tenure_exceeds_experience():
    # 1 job of 120 months but only 3 years of stated experience -> impossible
    rec = make_candidate(**{"profile.years_of_experience": 3.0})
    rec["career_history"][0]["duration_months"] = 120
    rep = _report(rec)
    assert rep.is_honeypot is True


def test_keyword_stuffer_gets_heavy_penalty():
    # Non-technical title, AI skills, no AI career evidence
    rec = make_candidate(
        **{"profile.current_title": "Marketing Manager"},
    )
    rec["career_history"][0]["title"] = "Marketing Manager"
    rec["career_history"][0]["description"] = "Ran marketing campaigns and managed budgets."
    rep = _report(rec)
    assert rep.is_honeypot is False
    assert rep.penalty < 0.5  # strongly down-weighted


def test_consulting_only_career_is_penalized():
    rec = make_candidate()
    for job in rec["career_history"]:
        job["company"] = "Infosys"
        job["industry"] = "IT Services"
    rep = _report(rec)
    assert rep.penalty < 1.0
    assert any("consulting" in r or "IT-services" in r for r in rep.penalty_reasons)
