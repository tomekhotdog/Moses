#!/usr/bin/env python3
"""Render a campaign as a per-iteration Markdown presentation.

Produces a single Markdown document that walks through each iteration of a Moses
loop campaign: the commit, the Score and violation deltas, and a simple ASCII
sparkline of the Score trajectory. Useful for sharing what an autonomous run
achieved.

Usage:
    python evals/build_per_iter_presentation.py <campaign.json> [-o out.md]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

_BLOCKS = "▁▂▃▄▅▆▇█"


def sparkline(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return _BLOCKS[0] * len(values)
    out = []
    for v in values:
        idx = int((v - lo) / (hi - lo) * (len(_BLOCKS) - 1))
        out.append(_BLOCKS[idx])
    return "".join(out)


def build(campaign: dict) -> str:
    baseline = campaign.get("baseline", {})
    best = campaign.get("best", {})
    iterations = campaign.get("iterations", [])

    scores = [baseline.get("score", 0)] + [
        it.get("score_after", baseline.get("score", 0)) for it in iterations
    ]

    lines: list[str] = []
    lines.append("# Moses Campaign — Per-Iteration Walkthrough\n")
    lines.append(f"- **Target:** `{campaign.get('target_path', 'src/')}`")
    lines.append(f"- **Branch:** {campaign.get('branch') or '(in-place)'}")
    lines.append(
        f"- **Baseline:** {baseline.get('score')} ({baseline.get('grade')}), "
        f"{baseline.get('violations')} violations"
    )
    lines.append(f"- **Best:** {best.get('score')} ({best.get('grade')})")
    lines.append(f"- **Trajectory:** `{sparkline(scores)}`  "
                 f"({scores[0]} → {scores[-1]})\n")
    lines.append("---\n")

    if not iterations:
        lines.append("_No iterations recorded yet._\n")
        return "\n".join(lines)

    for it in iterations:
        n = it.get("iteration")
        sb, sa = it.get("score_before"), it.get("score_after")
        vb, va = it.get("violations_before"), it.get("violations_after")
        delta = (sa - sb) if (sa is not None and sb is not None) else None
        arrow = "↑" if (delta or 0) > 0 else ("↓" if (delta or 0) < 0 else "→")
        lines.append(f"## Iteration {n} {arrow}\n")
        lines.append(f"- **Commit:** `{(it.get('commit') or '')[:12]}`")
        lines.append(f"- **Score:** {sb} → {sa}"
                     + (f"  ({delta:+.2f})" if delta is not None else ""))
        if vb is not None and va is not None:
            lines.append(f"- **Violations:** {vb} → {va}  ({va - vb:+d})")
        lines.append(f"- **Grade after:** {it.get('grade_after', '?')}")
        if it.get("regression"):
            lines.append("- ⚠️ **Recorded regression**")
        lines.append("")

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", help="path to campaign.json")
    parser.add_argument("-o", "--output", help="write Markdown here (default: stdout)")
    args = parser.parse_args(argv)

    campaign = json.loads(Path(args.campaign).read_text(encoding="utf-8"))
    md = build(campaign)
    if args.output:
        Path(args.output).write_text(md, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
