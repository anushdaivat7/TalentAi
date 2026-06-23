"""Scoring tests: range, role-fit decisiveness, honeypot suppression."""
from talentai.features import extract_features
from talentai.scoring import score_candidate
from talentai.traps import detect
from tests.factory import make_candidate


def _score(rec, semantic=None):
    cf = extract_features(rec)
    return score_candidate(cf, semantic=semantic, trap=detect(cf))


def test_score_in_unit_range():
    sb = _score(make_candidate())
    assert 0.0 <= sb.final_score <= 1.0


def test_strong_candidate_scores_high():
    sb = _score(make_candidate())
    assert sb.final_score >= 0.6


def test_honeypot_scored_to_zero():
    rec = make_candidate(skills=[
        {"name": "Embeddings", "proficiency": "expert", "endorsements": 0, "duration_months": 0},
        {"name": "FAISS", "proficiency": "expert", "endorsements": 0, "duration_months": 0},
        {"name": "Retrieval", "proficiency": "expert", "endorsements": 0, "duration_months": 0},
    ])
    sb = _score(rec)
    assert sb.final_score == 0.0


def test_role_fit_beats_keyword_stuffer():
    """An AI engineer should outrank a keyword-stuffing Marketing Manager."""
    good = _score(make_candidate(cid="CAND_0000001"))

    stuffer = make_candidate(cid="CAND_0000002",
                             **{"profile.current_title": "Marketing Manager"})
    stuffer["career_history"][0]["title"] = "Marketing Manager"
    stuffer["career_history"][0]["description"] = "Managed marketing campaigns."
    bad = _score(stuffer)

    assert good.final_score > bad.final_score


def test_semantic_blends_in():
    low = _score(make_candidate(), semantic=0.1).final_score
    high = _score(make_candidate(), semantic=0.95).final_score
    assert high >= low
