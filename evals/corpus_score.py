"""Score every solution in a corpus tree with Moses -> moses_scores.json.

Deterministic half of the calibration corpus: walks ``<corpus>/<qid>/*.py``
(each question dir, e.g. ``2024_q4``, embeds the year in its name), runs
``moses.engine.run`` on each solution file, and records Score/grade/per-rule
contributions. The LLM-judge half is produced separately (see corpus_report.py).

Usage: uv run python evals/corpus_score.py --corpus evals/corpus
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from moses.config import Config
from moses.engine import run


def score_corpus(corpus_root: Path) -> dict:
    """Score all question solutions under ``corpus_root`` and return the data dict.

    A question dir is any immediate subdirectory containing a ``problem.md``.
    """
    corpus_root = Path(corpus_root)
    out: dict = {"questions": {}}
    qdirs = sorted(
        p for p in corpus_root.iterdir() if p.is_dir() and (p / "problem.md").exists()
    )
    for qdir in qdirs:
        solutions: dict = {}
        for sol in sorted(qdir.glob("*.py")):
            verdict = run(sol, Config())
            commandments = {
                str(c.number): c.score_contribution
                for c in verdict.commandments
                if c.status == "measured"
            }
            solutions[sol.name] = {
                "loc": verdict.overview["non_blank_loc"],
                "moses_score": round(verdict.score, 2),
                "grade": verdict.grade,
                "commandments": commandments,
            }
        out["questions"][qdir.name] = solutions
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="evals/corpus", help="Corpus root directory")
    args = parser.parse_args(argv)

    corpus_root = Path(args.corpus)
    data = score_corpus(corpus_root)
    out_path = corpus_root / "moses_scores.json"
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(data['questions'])} questions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
