"""Commandment 11 — Small functions.

Metric: p95 of non-blank LOC per function.
Curve:  100 − 2·max(0, p95 − 50).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_functions, percentile

NUMBER = 11
NAME = "Small functions"


@dataclass(frozen=True)
class RuleConfig:
    loc_budget: int = 50
    slope: float = 2.0
    violation_threshold: int = 50


class SmallFunctions:
    number = NUMBER
    name = NAME
    RuleConfig = RuleConfig

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult:
        funcs = list(iter_functions(codebase))
        if not funcs:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        locs = [f.non_blank_loc for f in funcs]
        p95 = percentile(locs, 95)
        score = clamp(100 - config.slope * max(0, p95 - config.loc_budget))

        violations = sorted(
            (
                {
                    "file": f.file.relpath,
                    "line": f.lineno,
                    "function": f.qualname or f.name,
                    "loc": f.non_blank_loc,
                }
                for f in funcs
                if f.non_blank_loc > config.violation_threshold
            ),
            key=lambda v: v["loc"],
            reverse=True,
        )[:50]

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(p95, 2),
            score_contribution=score,
            status="measured",
            detail={"p95_loc": round(p95, 2), "function_count": len(funcs)},
            violations=violations,
        )
