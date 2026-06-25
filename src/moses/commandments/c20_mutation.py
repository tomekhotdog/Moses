"""Commandment 20 — Mutation kill rate.

Opt-in via --deep. Shells out to mutmut. Disabled by default (the engine skips
it unless config.deep). Metric: kill rate in [0,1]. Curve: 100·M.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass

from ..models import CommandmentResult

NUMBER = 20
NAME = "Mutation kill rate"


@dataclass(frozen=True)
class Params:
    pass


class MutationKillRate:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params) -> CommandmentResult:
        binary = shutil.which("mutmut")
        if binary is None:
            return CommandmentResult(
                NUMBER,
                NAME,
                self.weight,
                status="not_measured",
                detail={"reason": "mutmut not installed"},
            )

        try:
            subprocess.run(
                [binary, "run"],
                cwd=str(codebase.root),
                capture_output=True,
                text=True,
                timeout=1800,
            )
            results = subprocess.run(
                [binary, "results", "--json"],
                cwd=str(codebase.root),
                capture_output=True,
                text=True,
                timeout=60,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return CommandmentResult(
                NUMBER,
                NAME,
                self.weight,
                status="error",
                detail={"error": str(exc)},
            )

        kill_rate = _parse_kill_rate(results.stdout)
        if kill_rate is None:
            return CommandmentResult(
                NUMBER,
                NAME,
                self.weight,
                status="not_measured",
                detail={"reason": "could not parse mutmut output"},
            )

        score = max(0.0, min(100.0, 100.0 * kill_rate))
        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(kill_rate, 3),
            score_contribution=score,
            status="measured",
            detail={"kill_rate": round(kill_rate, 3)},
            violations=[],
        )


def _parse_kill_rate(stdout: str) -> float | None:
    try:
        data = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        return None
    killed = data.get("killed", 0)
    survived = data.get("survived", 0)
    total = killed + survived
    if total == 0:
        return None
    return killed / total
