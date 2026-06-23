"""Submission tests: ranking monotonicity, tie-breaks, CSV format."""
import csv

from talentai.ranker import rank_records
from talentai.submission import write_submission
from tests.factory import make_candidate


def _pool(n=12):
    recs = []
    for i in range(1, n + 1):
        rec = make_candidate(cid=f"CAND_{i:07d}")
        # vary experience so scores differ
        rec["profile"]["years_of_experience"] = 4.0 + (i % 6)
        recs.append(rec)
    return recs


def test_ranks_are_unique_and_sequential():
    ranked = rank_records(_pool(), top_k=10)
    ranks = [r["rank"] for r in ranked]
    assert ranks == list(range(1, len(ranked) + 1))


def test_scores_non_increasing_by_rank():
    ranked = rank_records(_pool(), top_k=10)
    scores = [r["score_raw"] for r in sorted(ranked, key=lambda r: r["rank"])]
    assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))


def test_tie_break_candidate_id_ascending():
    # All identical -> equal scores -> must order by candidate_id ascending
    ranked = rank_records(_pool(6), top_k=6)
    by_rank = sorted(ranked, key=lambda r: r["rank"])
    for a, b in zip(by_rank, by_rank[1:]):
        if a["score_raw"] == b["score_raw"]:
            assert a["candidate_id"] < b["candidate_id"]


def test_written_csv_has_correct_header_and_quoting(tmp_path):
    ranked = rank_records(_pool(), top_k=10)
    out = tmp_path / "sub.csv"
    write_submission(ranked, out_path=out)

    with open(out, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["candidate_id", "rank", "score", "reasoning"]
    assert len(rows) - 1 == 10  # header + 10 data rows
    # score column parses as float and is non-increasing
    scores = [float(r[2]) for r in rows[1:]]
    assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))


def test_reasoning_is_non_empty_and_varied(tmp_path):
    ranked = rank_records(_pool(), top_k=10)
    reasons = [r["explanation"] for r in ranked]
    assert all(reasons)                      # none empty
    assert len(set(reasons)) > 1             # not all identical
