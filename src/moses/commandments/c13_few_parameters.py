"""Commandment 13 — Few parameters.

Metric: mean param count across all functions, excluding self/cls and dunders.
Curve:  100 − 25·max(0, M − 2).
"""

from __future__ import annotations

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_dunder, iter_functions, mean, param_names

NUMBER = 13
NAME = "Few parameters"
PARAM_BUDGET = 2
VIOLATION_THRESHOLD = 4


class FewParameters:
    number = NUMBER
    name = NAME

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase) -> CommandmentResult:
        counts = []
        violations = []
        for f in iter_functions(codebase):
            if is_dunder(f.name):
                continue
            n = len(param_names(f.node, skip_self=True))
            counts.append(n)
            if n >= VIOLATION_THRESHOLD:
                violations.append(
                    {
                        "file": f.file.relpath,
                        "line": f.lineno,
                        "function": f.qualname or f.name,
                        "params": n,
                    }
                )

        if not counts:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(counts)
        score = clamp(100 - 25 * max(0, m - PARAM_BUDGET))
        violations.sort(key=lambda v: v["params"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_params": round(m, 2), "function_count": len(counts)},
            violations=violations[:50],
        )
