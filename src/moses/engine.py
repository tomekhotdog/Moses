"""The scorer: iterates ALL_COMMANDMENTS over a Codebase and builds a Verdict.

Pure-Python, deterministic, no network calls. Each rule is wrapped in its own
try/except: a rule that raises is downgraded to ``status="error"`` rather than
crashing the run. The Score averages only over **enabled, measured** rules.
"""

from __future__ import annotations

import platform
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone

from . import __version__
from .commandments import ALL_COMMANDMENTS
from .commandments.base import not_measured
from .commandments.descriptions import DESCRIPTIONS
from .config import Config
from .loader import load_codebase
from .models import Codebase, CommandmentResult, Verdict, grade_for

HOTSPOT_LIMIT = 15


def _git_commit(root) -> str | None:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            timeout=5,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def _weighted_score(results: list[CommandmentResult], config: Config) -> float:
    """Q = Σ (wᵢ · Sᵢ) / Σ wᵢ over enabled, measured rules only."""
    num = 0.0
    den = 0
    for r in results:
        if r.status != "measured":
            continue
        if not config.is_enabled(r.number):
            continue
        w = config.commandments.weight_for(r.number)
        num += w * r.score_contribution
        den += w
    if den == 0:
        return 100.0
    return num / den


def _build_hotspots(results: list[CommandmentResult], config: Config) -> list[dict]:
    """Aggregate per-file Score-drag from violations, weighted by rule Weight.

    Severity for a file = Σ over rules of weight · (100 - score) · share_of_violations.
    A simpler proxy: weight · violation_count, accumulated per file.
    """
    drag: dict[str, float] = defaultdict(float)
    hits: dict[str, Counter] = defaultdict(Counter)
    for r in results:
        if r.status != "measured" or not r.violations:
            continue
        deficit = max(0.0, 100.0 - r.score_contribution)
        per_v = (config.commandments.weight_for(r.number) * deficit) / max(1, len(r.violations))
        for v in r.violations:
            f = v.get("file")
            if not f:
                continue
            drag[f] += per_v
            hits[f][r.number] += 1
    hotspots = [
        {
            "file": f,
            "severity": round(sev, 2),
            "commandment_hits": dict(hits[f]),
        }
        for f, sev in drag.items()
    ]
    hotspots.sort(key=lambda h: h["severity"], reverse=True)
    return hotspots[:HOTSPOT_LIMIT]


def _overview(codebase: Codebase) -> dict:
    return {
        "file_count": len(codebase.files),
        "loc": codebase.total_loc,
        "non_blank_loc": codebase.non_blank_loc,
        "language_mix": {"python": len(codebase.files)},
    }


def run(root, config: Config | None = None) -> Verdict:
    """Run all Commandments over the tree at ``root`` and return a Verdict."""
    config = config or Config()
    codebase = load_codebase(root, excludes=config.excludes)

    implemented = {c.number: c for c in ALL_COMMANDMENTS}
    results: list[CommandmentResult] = []

    for number in sorted(DESCRIPTIONS.keys()):
        name = DESCRIPTIONS[number][0]
        if not config.is_enabled(number):
            # Disabled rules still appear, but with not_measured status so they
            # never count toward the Score.
            results.append(not_measured(number, name))
            continue
        cmd = implemented.get(number)
        if cmd is None:
            results.append(not_measured(number, name))
            continue
        rule_config = config.commandments.config_for(number)
        if rule_config is None:
            rule_config = cmd.RuleConfig()
        try:
            result = cmd.evaluate(codebase, rule_config)
        except Exception as exc:  # noqa: BLE001 - deliberately broad; one bad rule must not crash the run
            result = CommandmentResult(
                number=number,
                name=name,
                weight=config.commandments.weight_for(number),
                metric=None,
                score_contribution=100.0,
                status="error",
                detail={"error": f"{type(exc).__name__}: {exc}"},
                violations=[],
            )
        results.append(result)

    score = _weighted_score(results, config)
    grade = grade_for(score)
    hotspots = _build_hotspots(results, config)
    overview = _overview(codebase)
    meta = {
        "tool_version": __version__,
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "commit": _git_commit(codebase.root),
        "platform": platform.platform(),
        "deep": config.deep,
    }

    return Verdict(
        score=score,
        grade=grade,
        commandments=results,
        hotspots=hotspots,
        overview=overview,
        meta=meta,
    )
