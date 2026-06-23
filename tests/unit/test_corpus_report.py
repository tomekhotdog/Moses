"""corpus_report: rank-agreement math and the merged comparison markdown."""

from __future__ import annotations

import json
from pathlib import Path

from evals.corpus_report import build_comparison, rank_agreement


def test_rank_agreement_perfect():
    pairs = [(10.0, 1.0), (20.0, 2.0), (30.0, 3.0)]
    assert rank_agreement(pairs)["spearman"] == 1.0


def test_rank_agreement_inverted():
    pairs = [(10.0, 3.0), (20.0, 2.0), (30.0, 1.0)]
    assert rank_agreement(pairs)["spearman"] == -1.0


def test_rank_agreement_too_few():
    assert rank_agreement([(10.0, 1.0)])["spearman"] is None


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    (root / "2024" / "q1").mkdir(parents=True)
    moses = {
        "year": "2024",
        "questions": {
            "q1": {
                "good.py": {"loc": 50, "moses_score": 85.0, "grade": "A", "commandments": {"27": 90.0}},
                "bad.py": {"loc": 40, "moses_score": 40.0, "grade": "D", "commandments": {"27": 10.0, "16": 0.0}},
            }
        },
    }
    (root / "moses_scores.json").write_text(json.dumps(moses), encoding="utf-8")
    judge = {
        "good.py": {"pct": 88, "justification": "Clean, well modelled."},
        "bad.py": {"pct": 30, "justification": "Stringly typed, duplicated."},
    }
    (root / "2024" / "q1" / "judgements.json").write_text(json.dumps(judge), encoding="utf-8")
    return root


def test_build_comparison_contains_rows_and_correlation(tmp_path):
    root = _corpus(tmp_path)
    md = build_comparison(root, "2024")
    assert "q1" in md
    assert "good.py" in md and "bad.py" in md
    assert "85.0" in md  # moses score present
    assert "88" in md     # judge pct present
    # good and bad agree in rank between moses and judge -> spearman 1.0
    assert "1.0" in md
