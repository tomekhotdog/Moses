"""corpus_score: run Moses over a corpus tree and emit moses_scores.json."""

from __future__ import annotations

import json
from pathlib import Path

from evals.corpus_score import score_corpus


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_score_corpus_shape(tmp_path):
    root = tmp_path / "corpus"
    _write(root / "2024_q1" / "problem.md", "# Q1\n")
    _write(root / "2024_q1" / "a.py", "def add(x: int, y: int) -> int:\n    return x + y\n")
    _write(root / "2024_q1" / "b.py", "x = 1\nclass C:\n    def m(self):\n        return x\n")
    result = score_corpus(root)
    q1 = result["questions"]["2024_q1"]
    assert set(q1) == {"a.py", "b.py"}
    for entry in q1.values():
        assert isinstance(entry["moses_score"], float)
        assert entry["grade"] in {"A", "B", "C", "D", "E", "F"}
        assert isinstance(entry["loc"], int) and entry["loc"] > 0
        assert isinstance(entry["commandments"], dict)


def test_score_corpus_writes_json(tmp_path):
    root = tmp_path / "corpus"
    _write(root / "2024_q1" / "problem.md", "# Q1\n")
    _write(root / "2024_q1" / "a.py", "def add(x: int, y: int) -> int:\n    return x + y\n")
    from evals.corpus_score import main

    rc = main(["--corpus", str(root)])
    assert rc == 0
    data = json.loads((root / "moses_scores.json").read_text())
    assert "2024_q1" in data["questions"]
