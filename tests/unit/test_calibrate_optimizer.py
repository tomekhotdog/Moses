"""Offline weight optimizer: recompute Moses scores from stored per-rule scores."""

from __future__ import annotations

from evals.calibrate import mean_per_question_spearman, optimize_weights, weighted_score


def test_weighted_score_basic():
    # two rules, equal weight -> mean
    assert weighted_score({"1": 80.0, "2": 100.0}, {1: 1, 2: 1}) == 90.0
    # weight skew
    assert weighted_score({"1": 0.0, "2": 100.0}, {1: 3, 2: 1}) == 25.0
    # empty -> 100.0 (matches engine convention)
    assert weighted_score({}, {1: 1}) == 100.0


def _data():
    # Two questions. Rule 1 ranks WITH the judge, rule 2 ranks AGAINST it.
    return {
        "questions": {
            "qA": {
                "good.py": {"commandments": {"1": 90.0, "2": 10.0}, "judge_pct": 90},
                "bad.py": {"commandments": {"1": 10.0, "2": 90.0}, "judge_pct": 20},
            },
            "qB": {
                "good.py": {"commandments": {"1": 80.0, "2": 20.0}, "judge_pct": 85},
                "bad.py": {"commandments": {"1": 20.0, "2": 80.0}, "judge_pct": 30},
            },
        }
    }


def test_mean_per_question_spearman_directions():
    data = _data()
    # weighting only rule 1 (judge-aligned) -> perfect agreement
    assert mean_per_question_spearman(data, {1: 1, 2: 0}) == 1.0
    # weighting only rule 2 (anti-aligned) -> inverted
    assert mean_per_question_spearman(data, {1: 0, 2: 1}) == -1.0


def test_optimize_improves_or_equals():
    data = _data()
    base = {1: 1, 2: 1}
    tuned, fit = optimize_weights(data, base)
    base_fit = mean_per_question_spearman(data, base)
    assert fit >= base_fit
    # it should discover rule 1 deserves more weight than rule 2
    assert tuned[1] >= tuned[2]
