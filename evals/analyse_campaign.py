#!/usr/bin/env python3
"""Summarise a Moses loop campaign.

Reads a ``campaign.json`` audit trail and prints aggregate progress statistics:
total Score gain, per-iteration deltas, how many iterations actually improved
things, and the best result observed.

Usage:
    python evals/analyse_campaign.py <path-to-campaign.json> [--json]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def summarise(campaign: dict) -> dict:
    baseline = campaign.get("baseline", {})
    best = campaign.get("best", {})
    iterations = campaign.get("iterations", [])

    deltas = [
        (it.get("score_after", 0) - it.get("score_before", 0))
        for it in iterations
        if it.get("score_after") is not None and it.get("score_before") is not None
    ]
    improving = sum(1 for d in deltas if d > 0)
    regressing = sum(1 for d in deltas if d < 0)

    base_score = baseline.get("score", 0) or 0
    final_score = iterations[-1].get("score_after", base_score) if iterations else base_score

    return {
        "baseline_score": base_score,
        "baseline_grade": baseline.get("grade"),
        "final_score": final_score,
        "best_score": best.get("score"),
        "best_grade": best.get("grade"),
        "total_gain": round(final_score - base_score, 2),
        "iterations": len(iterations),
        "improving_iterations": improving,
        "regressing_iterations": regressing,
        "mean_delta": round(sum(deltas) / len(deltas), 3) if deltas else 0.0,
        "max_single_gain": round(max(deltas), 2) if deltas else 0.0,
    }


def print_human(summary: dict, campaign: dict) -> None:
    print("Moses campaign summary")
    print("=" * 40)
    print(f"  baseline:    {summary['baseline_score']} ({summary['baseline_grade']})")
    print(f"  final:       {summary['final_score']}")
    print(f"  best:        {summary['best_score']} ({summary['best_grade']})")
    print(f"  total gain:  {summary['total_gain']:+}")
    print(f"  iterations:  {summary['iterations']} "
          f"({summary['improving_iterations']} up, {summary['regressing_iterations']} down)")
    print(f"  mean delta:  {summary['mean_delta']:+}")
    print(f"  best single: {summary['max_single_gain']:+}")
    print()
    print("Per-iteration:")
    for it in campaign.get("iterations", []):
        sb, sa = it.get("score_before"), it.get("score_after")
        delta = (sa - sb) if (sa is not None and sb is not None) else None
        mark = "+" if (delta or 0) > 0 else ("-" if (delta or 0) < 0 else "=")
        commit = (it.get("commit") or "")[:8]
        print(f"  #{it.get('iteration'):>3} {mark} {sb} -> {sa}  @ {commit}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", help="path to campaign.json")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args(argv)

    campaign = load(Path(args.campaign))
    summary = summarise(campaign)
    if args.json:
        print(json.dumps(summary, indent=2))
    else:
        print_human(summary, campaign)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
