"""Commandment 5 — Pull complexity downward.

Metric: mean count of required (no-default) public params per public top-level
function. Curve: 100 − 20·max(0, M − 1).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_private, mean, parse_file, required_param_count

NUMBER = 5
NAME = "Pull complexity downward"


@dataclass(frozen=True)
class Params:
    budget: float = 1.0
    slope: float = 20.0


class PullComplexityDown:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params) -> CommandmentResult:
        counts = []
        violations = []
        for source in codebase.files:
            tree = parse_file(source)
            if tree is None:
                continue
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if is_private(node.name):
                        continue
                    n = required_param_count(node, skip_self=True)
                    counts.append(n)
                    if n >= 3:
                        violations.append(
                            {
                                "file": source.relpath,
                                "line": node.lineno,
                                "function": node.name,
                                "required_params": n,
                            }
                        )

        if not counts:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(counts)
        score = clamp(100 - params.slope * max(0, m - params.budget))
        violations.sort(key=lambda v: v["required_params"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_required_params": round(m, 2), "function_count": len(counts)},
            violations=violations[:50],
        )
