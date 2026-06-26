"""Calibration harness (SCAFFOLDING). Reports current Moses-vs-Judge agreement.

The optimiser is intentionally a stub for now: it returns the default
CommandmentsConfig unchanged. The real search over CommandmentsConfig (rule
configs + weights) lands once the corpus is scaled beyond the 3-question pilot.

Usage: uv run python -m evals.calibrate --corpus evals/corpus
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


def report_baseline(corpus_root: Path) -> str:
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


def sharpen(score: float, gamma: float) -> float:
    """Global curve-harshness lever: gamma>1 spreads lenient scores downward."""
    s = max(0.0, min(100.0, score))
    return 100.0 * (s / 100.0) ** gamma


def weighted_score(commandments: dict, weights: dict, gamma: float = 1.0) -> float:
    """Re-aggregate stored per-rule score_contributions with candidate weights.

    Mirrors engine._weighted_score: mean over MEASURED rules only; 100.0 if none.
    Each per-rule score is sharpened by `gamma` before the weighted mean
    (gamma=1.0 is the identity transform, preserving the 2-arg behaviour).
    """
    num = 0.0
    den = 0.0
    for n_str, score in commandments.items():
        w = weights.get(int(n_str), 0)
        s = sharpen(score, gamma) if gamma != 1.0 else score
        num += w * s
        den += w
    return num / den if den else 100.0


def mean_per_question_spearman(
    data: dict,
    weights: dict,
    gamma: float = 1.0,
    question_ids: set | None = None,
) -> float:
    """Mean over questions of Spearman(moses-with-weights, judge) within each question.

    `gamma` sharpens per-rule scores before aggregation (1.0 = identity).
    `question_ids` restricts to those question ids (None = all questions).
    """
    from evals.corpus_report import rank_agreement

    rhos = []
    for qid, rows in data["questions"].items():
        if question_ids is not None and qid not in question_ids:
            continue
        pairs = []
        for r in rows.values():
            if r.get("judge_pct") is None:
                continue
            pairs.append(
                (weighted_score(r["commandments"], weights, gamma), float(r["judge_pct"]))
            )
        rho = rank_agreement(pairs)["spearman"]
        if rho is not None:
            rhos.append(rho)
    return round(sum(rhos) / len(rhos), 4) if rhos else 0.0


def load_splits(corpus_root: Path) -> dict:
    """Read <corpus>/splits.json -> {"train": [...], "validation": [...], "test": [...]}.

    Keys starting with '_' (comments) are ignored; missing splits default to [].
    """
    corpus_root = Path(corpus_root)
    raw = json.loads((corpus_root / "splits.json").read_text(encoding="utf-8"))
    clean = {k: v for k, v in raw.items() if not k.startswith("_")}
    return {
        "train": clean.get("train", []),
        "validation": clean.get("validation", []),
        "test": clean.get("test", []),
    }


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


def optimize(
    data: dict,
    base_weights: dict,
    train_ids: set,
    *,
    reg_lambda: float = 0.05,
    weight_bounds: tuple[float, float] = (0.25, 4.0),
    gamma_choices: tuple[float, ...] = (0.75, 1.0, 1.5, 2.0, 2.5),
    passes: int = 6,
) -> tuple[dict, float, float]:
    """Coordinate ascent over per-rule weights (bounded to [lo,hi]*default, never 0)
    and a global gamma, maximising regularised mean per-question Spearman on train_ids.
    Regularised fitness = spearman(train) - reg_lambda * mean(((w-base)/base)**2).

    Deterministic. Returns (weights, gamma, train_fitness_regularised).
    """
    lo, hi = weight_bounds
    base = {n: float(base_weights[n]) for n in base_weights}
    bounds = {n: (lo * base[n], hi * base[n]) for n in base}

    def clamp(n: int, value: float) -> float:
        a, b = bounds[n]
        return round(max(a, min(b, value)), 4)

    def regularisation(weights: dict) -> float:
        terms = [((weights[n] - base[n]) / base[n]) ** 2 for n in base if base[n]]
        return sum(terms) / len(terms) if terms else 0.0

    def fitness(weights: dict, gamma: float) -> float:
        spear = mean_per_question_spearman(data, weights, gamma, question_ids=train_ids)
        return spear - reg_lambda * regularisation(weights)

    # Start from the default weights, clamped into range (no-op for defaults).
    weights = {n: clamp(n, base[n]) for n in base}
    gamma = 1.0
    best = fitness(weights, gamma)

    factors = (0.5, 0.75, 1.5, 2.0)
    for _ in range(passes):
        improved = False
        # Sweep gamma first.
        for g in gamma_choices:
            fit = fitness(weights, g)
            if fit > best:
                best, gamma, improved = fit, g, True
        # Sweep each rule's weight.
        for n in sorted(weights):
            current = weights[n]
            for f in factors:
                trial = dict(weights)
                trial[n] = clamp(n, current * f)
                if trial[n] == current:
                    continue
                fit = fitness(trial, gamma)
                if fit > best:
                    best, weights, improved = fit, trial, True
        if not improved:
            break
    return weights, gamma, best


def run_optimize(corpus_root: Path) -> str:
    """Split-aware offline weight + gamma tuning; write tuned config; return a report."""
    from moses.config import WEIGHTS

    corpus_root = Path(corpus_root)
    data = json.loads((corpus_root / "comparison.json").read_text(encoding="utf-8"))
    splits = load_splits(corpus_root)
    base = dict(WEIGHTS)

    train_ids = set(splits["train"])
    val_ids = set(splits["validation"])
    test_ids = set(splits["test"])

    # Baseline: default weights, gamma=1.0, per split.
    base_train = mean_per_question_spearman(data, base, 1.0, question_ids=train_ids)
    base_val = mean_per_question_spearman(data, base, 1.0, question_ids=val_ids)
    base_test = mean_per_question_spearman(data, base, 1.0, question_ids=test_ids)

    # Tune on TRAIN only.
    tuned, gamma, train_fit_reg = optimize(data, base, train_ids)

    tuned_train = mean_per_question_spearman(data, tuned, gamma, question_ids=train_ids)
    tuned_val = mean_per_question_spearman(data, tuned, gamma, question_ids=val_ids)
    tuned_test = mean_per_question_spearman(data, tuned, gamma, question_ids=test_ids)

    # Largest weight changes vs the default WEIGHTS (none are ever zeroed).
    changes = sorted(
        ((n, tuned[n] - base[n]) for n in base),
        key=lambda kv: kv[1],
    )
    ups = [c for c in reversed(changes) if c[1] > 1e-9][:8]
    downs = [c for c in changes if c[1] < -1e-9][:8]

    out = corpus_root / "calibrated_weights.json"
    out.write_text(
        json.dumps(
            {"gamma": gamma, "weights": {str(n): round(w, 2) for n, w in sorted(tuned.items())}},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def row(label: str, tr: float, va: float, te: float) -> str:
        return f"  {label:<10} train={tr:<8} validation={va:<8} test={te:<8}"

    core = (1, 5, 11, 14)
    lines = ["# Calibration optimizer (split-aware, regularized)", ""]
    lines.append("Mean per-question Spearman (higher = better):")
    lines.append(row("baseline", base_train, base_val, base_test))
    lines.append(row("tuned", tuned_train, tuned_val, tuned_test))
    lines.append("")
    lines.append(f"Chosen gamma (leniency knob): {gamma}")
    lines.append(f"Regularised train fitness:    {round(train_fit_reg, 4)}")
    lines.append("")
    lines.append("Top up-weighted rules (default -> tuned):")
    for n, d in ups:
        lines.append(f"  C{n}: {base[n]} -> {round(tuned[n], 2)}  ({d:+.2f})")
    lines.append("")
    lines.append("Top down-weighted rules (default -> tuned):")
    for n, d in downs:
        lines.append(f"  C{n}: {base[n]} -> {round(tuned[n], 2)}  ({d:+.2f})")
    lines.append("")
    lines.append("Complexity-control rules (must stay non-zero):")
    for n in core:
        lines.append(f"  C{n}: {base[n]} -> {round(tuned[n], 2)}  (bounded >= {round(0.25 * base[n], 2)})")
    lines.append("")
    lines.append(f"Wrote tuned config (gamma + weights) to {out}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="evals/corpus")
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Tune per-rule weights offline to maximise mean per-question Spearman.",
    )
    args = parser.parse_args(argv)
    if args.optimize:
        print(run_optimize(Path(args.corpus)))
    else:
        print(report_baseline(Path(args.corpus)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
