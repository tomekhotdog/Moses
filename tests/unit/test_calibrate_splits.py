from __future__ import annotations
import json
from evals.calibrate import sharpen, weighted_score, mean_per_question_spearman, optimize, load_splits


def test_sharpen_monotonic_and_spreads():
    assert sharpen(100, 2.0) == 100.0
    assert sharpen(0, 2.0) == 0.0
    assert sharpen(50, 2.0) == 25.0       # gamma>1 pushes mid scores down
    assert sharpen(50, 1.0) == 50.0


def test_weighted_score_gamma_default_unchanged():
    cmds = {"1": 80.0, "2": 40.0}
    assert weighted_score(cmds, {1: 1, 2: 1}) == weighted_score(cmds, {1: 1, 2: 1}, gamma=1.0)


def _data():
    return {"questions": {
        "qA": {"g.py": {"commandments": {"1": 90.0, "2": 10.0}, "judge_pct": 90},
               "b.py": {"commandments": {"1": 10.0, "2": 90.0}, "judge_pct": 20}},
        "qB": {"g.py": {"commandments": {"1": 80.0, "2": 20.0}, "judge_pct": 85},
               "b.py": {"commandments": {"1": 20.0, "2": 80.0}, "judge_pct": 30}},
    }}


def test_question_ids_filter():
    data = _data()
    # only qA, rule1-only weighting -> perfect
    assert mean_per_question_spearman(data, {1: 1, 2: 0}, question_ids={"qA"}) == 1.0


def test_optimize_respects_weight_bounds_no_zeroing():
    data = _data()
    base = {1: 4, 2: 4}
    w, gamma, fit = optimize(data, base, train_ids={"qA", "qB"}, reg_lambda=0.0)
    # never zeroed, never below 0.25x base, never above 4x base
    for n in base:
        assert w[n] >= 0.25 * base[n] - 1e-9
        assert w[n] <= 4.0 * base[n] + 1e-9
        assert w[n] > 0
    # rule 1 (judge-aligned) should end >= rule 2
    assert w[1] >= w[2]


def test_load_splits(tmp_path):
    root = tmp_path / "corpus"
    root.mkdir()
    (root / "splits.json").write_text(json.dumps({"_comment": "x", "train": ["a"], "validation": ["b"], "test": ["c"]}))
    s = load_splits(root)
    assert s["train"] == ["a"] and s["validation"] == ["b"] and s["test"] == ["c"]
    assert "_comment" not in s
