"""calibrate scaffolding: agreement metric + baseline report."""

from __future__ import annotations

import json
from pathlib import Path

from evals.calibrate import agreement, report_baseline


def test_agreement_perfect():
    a = agreement([(85.0, 88.0), (40.0, 30.0), (60.0, 70.0)])
    assert a["spearman"] == 1.0
    assert a["mean_abs_gap"] == round((3 + 10 + 10) / 3, 2)


def test_report_baseline_over_corpus(tmp_path):
    root = tmp_path / "corpus"
    (root / "2024" / "q1").mkdir(parents=True)
    merged = {
        "year": "2024",
        "questions": {
            "q1": {
                "good.py": {"moses_score": 85.0, "judge_pct": 88},
                "bad.py": {"moses_score": 40.0, "judge_pct": 30},
            }
        },
    }
    (root / "comparison.json").write_text(json.dumps(merged), encoding="utf-8")
    out = report_baseline(root)
    assert "q1" in out
    assert "spearman" in out.lower()
