"""Calibration harness (SCAFFOLDING). Reports current Moses-vs-Judge agreement.

The optimiser is intentionally a stub for now: it returns the default
CommandmentsConfig unchanged. The real search over CommandmentsConfig (rule
configs + weights) lands once the corpus is scaled beyond the 3-question pilot.

Usage: uv run python -m evals.calibrate --corpus evals/corpus --year 2024
(run via -m: this module imports the sibling evals.corpus_report package, which
the path form `python evals/calibrate.py` cannot resolve.)
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


def weighted_score(commandments: dict, weights: dict) -> float:
    """Re-aggregate stored per-rule score_contributions with candidate weights.

    Mirrors engine._weighted_score: mean over MEASURED rules only; 100.0 if none.
    """
    num = 0.0
    den = 0.0
    for n_str, score in commandments.items():
        w = weights.get(int(n_str), 0)
        num += w * score
        den += w
    return num / den if den else 100.0


def mean_per_question_spearman(data: dict, weights: dict) -> float:
    """Mean over questions of Spearman(moses-with-weights, judge) within each question."""
    from evals.corpus_report import rank_agreement

    rhos = []
    for rows in data["questions"].values():
        pairs = []
        for r in rows.values():
            if r.get("judge_pct") is None:
                continue
            pairs.append((weighted_score(r["commandments"], weights), float(r["judge_pct"])))
        rho = rank_agreement(pairs)["spearman"]
        if rho is not None:
            rhos.append(rho)
    return round(sum(rhos) / len(rhos), 4) if rhos else 0.0


def optimize_weights(data: dict, base_weights: dict, passes: int = 6) -> tuple[dict, float]:
    """Coordinate-ascent over integer-ish weights to maximise mean per-question Spearman.

    Deterministic: for each rule, try a fixed set of multiplicative/additive moves,
    keep any that improve fitness. Repeats for `passes` sweeps or until no change.
    """
    weights = dict(base_weights)
    best = mean_per_question_spearman(data, weights)
    candidates_factor = (0.0, 0.5, 2.0, 3.0)
    for _ in range(passes):
        improved = False
        for n in sorted(weights):
            current = weights[n]
            for f in candidates_factor:
                trial = dict(weights)
                trial[n] = max(0.0, round(current * f, 2)) if f != 0.0 else 0.0
                fit = mean_per_question_spearman(data, trial)
                if fit > best:
                    best, weights, improved = fit, trial, True
            # also try a small additive bump
            for delta in (-1.0, 1.0):
                trial = dict(weights)
                trial[n] = max(0.0, weights[n] + delta)
                fit = mean_per_question_spearman(data, trial)
                if fit > best:
                    best, weights, improved = fit, trial, True
        if not improved:
            break
    return weights, best


def run_optimize(corpus_root: Path, year: str = "2024") -> str:
    """Optimise per-rule weights offline; write tuned weights; return a report."""
    from moses.config import WEIGHTS

    corpus_root = Path(corpus_root)
    data = json.loads((corpus_root / "comparison.json").read_text(encoding="utf-8"))
    base = dict(WEIGHTS)

    baseline_fit = mean_per_question_spearman(data, base)
    tuned, tuned_fit = optimize_weights(data, base)

    # Largest weight changes vs the default WEIGHTS.
    changes = sorted(
        ((n, tuned.get(n, 0.0) - base.get(n, 0.0)) for n in set(base) | set(tuned)),
        key=lambda kv: kv[1],
    )
    ups = [c for c in reversed(changes) if c[1] > 0][:8]
    downs = [c for c in changes if c[1] < 0][:8]

    out = corpus_root / "calibrated_weights.json"
    out.write_text(
        json.dumps({str(n): round(w, 2) for n, w in sorted(tuned.items())}, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = ["# Calibration optimizer (offline weight tuning)", ""]
    lines.append(f"Baseline mean per-question Spearman:  {baseline_fit}")
    lines.append(f"Optimized mean per-question Spearman: {tuned_fit}")
    lines.append("")
    lines.append("Top up-weighted rules (default -> tuned):")
    for n, d in ups:
        lines.append(f"  C{n}: {base.get(n, 0)} -> {round(tuned.get(n, 0.0), 2)}  ({d:+.2f})")
    lines.append("")
    lines.append("Top down-weighted rules (default -> tuned):")
    for n, d in downs:
        lines.append(f"  C{n}: {base.get(n, 0)} -> {round(tuned.get(n, 0.0), 2)}  ({d:+.2f})")
    lines.append("")
    lines.append(f"Wrote tuned weights to {out}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="evals/corpus")
    parser.add_argument("--year", default="2024")
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Tune per-rule weights offline to maximise mean per-question Spearman.",
    )
    args = parser.parse_args(argv)
    if args.optimize:
        print(run_optimize(Path(args.corpus), args.year))
    else:
        print(report_baseline(Path(args.corpus), args.year))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
