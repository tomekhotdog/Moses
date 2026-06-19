#!/usr/bin/env python3
"""Campaign audit-trail recorder and validator for the Moses loop.

Two sub-commands, both operating on ``campaign.json``:

  record    Append one iteration record and update ``best``. Used by ralph.sh
            after a verified, committed improvement.

  validate  Check the whole audit trail for internal consistency and against the
            actual git history. Exits non-zero if any invariant is violated.

Invariants enforced by ``validate``:
  - schema_version is the expected value.
  - baseline has a numeric score.
  - every iteration references a commit that exists in the repo.
  - score continuity: each iteration's score_before equals the previous
    iteration's score_after (baseline for the first).
  - monotonicity of recorded improvements: an iteration that raised violations
    without a ``regression`` flag is illegal (the harness must revert, not
    record, regressions).
  - ``best`` is at least as high as any observed score.

The recorder is deliberately the only writer of campaign.json during a run, so
the file stays a trustworthy, append-only ledger.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _save(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _commit_exists(repo: Path, commit: str) -> bool:
    proc = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=str(repo),
        capture_output=True,
    )
    return proc.returncode == 0


# --------------------------------------------------------------------------- #
# record
# --------------------------------------------------------------------------- #


def cmd_record(args: argparse.Namespace) -> int:
    path = Path(args.campaign)
    campaign = _load(path)

    score_after = float(args.score_after)
    viol_after = int(args.violations_after)
    score_before = float(args.score_before)
    viol_before = int(args.violations_before)

    record = {
        "iteration": args.iteration,
        "commit": args.commit,
        "timestamp": _now(),
        "score_before": score_before,
        "score_after": score_after,
        "violations_before": viol_before,
        "violations_after": viol_after,
        "grade_after": args.grade_after,
        "regression": score_after < score_before or viol_after > viol_before,
    }
    campaign.setdefault("iterations", []).append(record)

    best = campaign.get("best") or {}
    if score_after >= float(best.get("score", -1)):
        campaign["best"] = {
            "score": score_after,
            "grade": args.grade_after,
            "violations": viol_after,
            "commit": args.commit,
            "timestamp": record["timestamp"],
        }

    _save(path, campaign)
    print(f"recorded iteration {args.iteration}: {score_before} -> {score_after}")
    return 0


# --------------------------------------------------------------------------- #
# validate
# --------------------------------------------------------------------------- #


def _problems(campaign: dict, repo: Path):
    if campaign.get("schema_version") != SCHEMA_VERSION:
        yield f"schema_version {campaign.get('schema_version')} != {SCHEMA_VERSION}"

    baseline = campaign.get("baseline") or {}
    if not isinstance(baseline.get("score"), (int, float)):
        yield "baseline.score missing or non-numeric"

    iterations = campaign.get("iterations", [])
    prev_after = baseline.get("score")
    observed_max = baseline.get("score", 0) or 0

    for i, it in enumerate(iterations):
        idx = it.get("iteration", i)
        for key in ("commit", "score_before", "score_after"):
            if key not in it:
                yield f"iteration {idx}: missing '{key}'"
                continue

        commit = it.get("commit")
        if commit and not _commit_exists(repo, commit):
            yield f"iteration {idx}: commit {commit[:8]} not in repo"

        sb = it.get("score_before")
        if prev_after is not None and sb is not None and abs(sb - prev_after) > 0.01:
            yield f"iteration {idx}: score_before {sb} != prior score_after {prev_after}"

        vb, va = it.get("violations_before"), it.get("violations_after")
        if vb is not None and va is not None and va > vb and not it.get("regression"):
            yield f"iteration {idx}: violations {vb}->{va} without regression flag"

        sa = it.get("score_after")
        if sa is not None:
            observed_max = max(observed_max, sa)
            prev_after = sa

    best = campaign.get("best") or {}
    if "score" in best and best["score"] < observed_max - 0.01:
        yield f"best.score {best['score']} below observed max {observed_max}"


def cmd_validate(args: argparse.Namespace) -> int:
    campaign = _load(Path(args.campaign))
    repo = Path(args.repo)
    problems = list(_problems(campaign, repo))
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    n = len(campaign.get("iterations", []))
    base = (campaign.get("baseline") or {}).get("score")
    best = (campaign.get("best") or {}).get("score")
    print(f"OK: {n} iteration(s), baseline {base} -> best {best}")
    return 0


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    rec = sub.add_parser("record", help="append an iteration record")
    rec.add_argument("--campaign", required=True)
    rec.add_argument("--iteration", type=int, required=True)
    rec.add_argument("--commit", required=True)
    rec.add_argument("--score-before", required=True)
    rec.add_argument("--score-after", required=True)
    rec.add_argument("--violations-before", required=True)
    rec.add_argument("--violations-after", required=True)
    rec.add_argument("--grade-after", default="?")
    rec.set_defaults(func=cmd_record)

    val = sub.add_parser("validate", help="validate the campaign trail")
    val.add_argument("--campaign", required=True)
    val.add_argument("--repo", required=True)
    val.set_defaults(func=cmd_validate)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
