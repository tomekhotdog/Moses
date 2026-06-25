"""Commandment 6 — Define errors out of existence.

Per public function: distinct exception types raised + nullable return paths
(`return None` branches when other branches return values). Mean.
Curve: 100 − 50·M (0 at ≥ 2).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_private, iter_functions, mean

NUMBER = 6
NAME = "Define errors out of existence"


@dataclass(frozen=True)
class RuleConfig:
    slope: float = 50.0


def _raised_types(node) -> set[str]:
    types: set[str] = set()
    for child in ast.walk(node):
        if isinstance(child, ast.Raise) and child.exc is not None:
            exc = child.exc
            if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                types.add(exc.func.id)
            elif isinstance(exc, ast.Name):
                types.add(exc.id)
    return types


def _has_nullable_return_mix(node) -> bool:
    returns_value = False
    returns_none = False
    for child in ast.walk(node):
        if isinstance(child, ast.Return):
            if child.value is None:
                returns_none = True
            elif isinstance(child.value, ast.Constant) and child.value.value is None:
                returns_none = True
            else:
                returns_value = True
    return returns_value and returns_none


class DefineErrorsOut:
    number = NUMBER
    name = NAME
    RuleConfig = RuleConfig

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult:
        scores = []
        violations = []
        for f in iter_functions(codebase):
            if is_private(f.name):
                continue
            raised = len(_raised_types(f.node))
            nullable = 1 if _has_nullable_return_mix(f.node) else 0
            failure_modes = raised + nullable
            scores.append(failure_modes)
            if failure_modes >= 2:
                violations.append(
                    {
                        "file": f.file.relpath,
                        "line": f.lineno,
                        "function": f.qualname or f.name,
                        "failure_modes": failure_modes,
                    }
                )

        if not scores:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(scores)
        score = clamp(100 - config.slope * m)
        violations.sort(key=lambda v: v["failure_modes"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_failure_modes": round(m, 2), "function_count": len(scores)},
            violations=violations[:50],
        )
