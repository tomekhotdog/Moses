"""Merge Moses scores with LLM-judge scores into a comparison report.

Reads ``<corpus>/moses_scores.json`` (from corpus_score.py) and each
``<corpus>/<qid>/judgements.json`` (agentic LLM-judge output), and writes a
single ``comparison.md`` (plus merged ``comparison.json``) laying the deterministic
Moses Score beside the holistic Judge score, with a per-question rank-agreement
summary.

Usage: uv run python evals/corpus_report.py --corpus evals/corpus
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _ranks(xs: list[float]) -> list[float]:
    """Average (tie-corrected) 1-based ranks."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    denom = (va * vb) ** 0.5
    return cov / denom if denom else 0.0


def rank_agreement(pairs: list[tuple[float, float]]) -> dict:
    """Spearman rho between the Moses and Judge scores in ``pairs``."""
    if len(pairs) < 2:
        return {"spearman": None, "n": len(pairs)}
    moses = [p[0] for p in pairs]
    judge = [p[1] for p in pairs]
    rho = _pearson(_ranks(moses), _ranks(judge))
    return {"spearman": round(rho, 3), "n": len(pairs)}


def merge(corpus_root: Path) -> dict:
    """Merge Moses + judge data into one structure keyed by question/solution."""
    corpus_root = Path(corpus_root)
    moses = json.loads((corpus_root / "moses_scores.json").read_text(encoding="utf-8"))
    merged: dict = {"questions": {}}
    for qname, sols in moses["questions"].items():
        jpath = corpus_root / qname / "judgements.json"
        judge = json.loads(jpath.read_text(encoding="utf-8")) if jpath.exists() else {}
        rows = {}
        for fname, m in sols.items():
            j = judge.get(fname, {})
            rows[fname] = {
                "loc": m["loc"],
                "moses_score": m["moses_score"],
                "grade": m["grade"],
                "commandments": m["commandments"],
                "judge_pct": j.get("pct"),
                "judge_justification": j.get("justification", ""),
            }
        merged["questions"][qname] = rows
    return merged


def _weakest(commandments: dict, k: int = 3) -> str:
    """The k lowest-scoring measured commandments, as 'N:score' tags."""
    items = sorted(commandments.items(), key=lambda kv: kv[1])[:k]
    return ", ".join(f"#{n}:{int(round(s))}" for n, s in items) if items else "—"


def build_comparison(corpus_root: Path) -> str:
    """Render the merged corpus as a Markdown comparison report."""
    data = merge(corpus_root)
    lines = ["# Calibration corpus — Moses vs Judge", ""]
    summary: list[str] = []
    for qname, rows in data["questions"].items():
        lines.append(f"## {qname}")
        lines.append("")
        lines.append("| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |")
        lines.append("|---|---|---|---|---|---|---|---|")
        pairs: list[tuple[float, float]] = []
        for fname, r in sorted(rows.items(), key=lambda kv: (kv[1]["judge_pct"] is None, -(kv[1]["judge_pct"] or 0))):
            judge = r["judge_pct"]
            gap = "" if judge is None else f"{r['moses_score'] - judge:+.1f}"
            if judge is not None:
                pairs.append((r["moses_score"], float(judge)))
            just = r["judge_justification"].replace("|", "\\|")
            judge_s = "—" if judge is None else str(judge)
            lines.append(
                f"| {fname} | {r['loc']} | {r['moses_score']} | {r['grade']} | "
                f"{judge_s} | {gap} | {_weakest(r['commandments'])} | {just} |"
            )
        agree = rank_agreement(pairs)
        rho = agree["spearman"]
        rho_s = "n/a" if rho is None else str(rho)
        lines.append("")
        lines.append(f"Rank agreement (Spearman ρ, Moses vs Judge): **{rho_s}** (n={agree['n']})")
        lines.append("")
        summary.append(f"| {qname} | {rho_s} | {agree['n']} |")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Question | Spearman ρ | n |")
    lines.append("|---|---|---|")
    lines.extend(summary)
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="evals/corpus")
    args = parser.parse_args(argv)

    corpus_root = Path(args.corpus)
    merged = merge(corpus_root)
    (corpus_root / "comparison.json").write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    md = build_comparison(corpus_root)
    (corpus_root / "comparison.md").write_text(md, encoding="utf-8")
    print(f"Wrote {corpus_root / 'comparison.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
