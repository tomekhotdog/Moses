"""Calibration harness (SCAFFOLDING). Reports current Moses-vs-Judge agreement.

The optimiser is intentionally a stub for now: it returns the default
CommandmentsConfig unchanged. The real search over CommandmentsConfig (rule
configs + weights) lands once the corpus is scaled beyond the 3-question pilot.

Usage: uv run python evals/calibrate.py --corpus evals/corpus --year 2024
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evals.corpus_report import rank_agreement


def agreement(pairs: list[tuple[float, float]]) -> dict:
    """Spearman rho + mean absolute (Moses - Judge) gap over (moses, judge) pairs."""
    rho = rank_agreement(pairs)["spearman"]
    gap = round(sum(abs(m - j) for m, j in pairs) / len(pairs), 2) if pairs else None
    return {"spearman": rho, "mean_abs_gap": gap, "n": len(pairs)}


def report_baseline(corpus_root: Path, year: str = "2024") -> str:
    """Human-readable report of current agreement per question + overall."""
    corpus_root = Path(corpus_root)
    data = json.loads((corpus_root / "comparison.json").read_text(encoding="utf-8"))
    lines = ["# Calibration baseline (Moses vs Judge)", ""]
    all_pairs: list[tuple[float, float]] = []
    for qname, rows in data["questions"].items():
        pairs = [
            (r["moses_score"], float(r["judge_pct"]))
            for r in rows.values()
            if r.get("judge_pct") is not None
        ]
        all_pairs.extend(pairs)
        a = agreement(pairs)
        lines.append(
            f"- {qname}: spearman={a['spearman']} mean_abs_gap={a['mean_abs_gap']} (n={a['n']})"
        )
    overall = agreement(all_pairs)
    lines.append("")
    lines.append(
        f"Overall: spearman={overall['spearman']} mean_abs_gap={overall['mean_abs_gap']} (n={overall['n']})"
    )
    return "\n".join(lines)


def optimize(corpus_root: Path, year: str = "2024"):
    """STUB. Returns the default CommandmentsConfig unchanged.

    TODO(phase-2b): search CommandmentsConfig (rule configs + weights) to minimise
    mean_abs_gap / maximise spearman across the corpus, re-scoring via
    moses.engine.run with the candidate config. Requires the larger corpus.
    """
    from moses.config import CommandmentsConfig

    return CommandmentsConfig.default()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="evals/corpus")
    parser.add_argument("--year", default="2024")
    args = parser.parse_args(argv)
    print(report_baseline(Path(args.corpus), args.year))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
