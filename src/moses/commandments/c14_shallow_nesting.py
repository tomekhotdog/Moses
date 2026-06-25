"""Commandment 14 — Shallow nesting.

Metric: p95 of max nesting depth across functions.
Counts If/For/While/Try/With/AsyncFor/AsyncWith.
Curve:  100 − 25·max(0, p95 − 2).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_functions, percentile

NUMBER = 14
NAME = "Shallow nesting"


@dataclass(frozen=True)
class RuleConfig:
    depth_budget: int = 2
    slope: float = 25.0
    violation_threshold: int = 3


_NESTING = (
    ast.If,
    ast.For,
    ast.While,
    ast.Try,
    ast.With,
    ast.AsyncFor,
    ast.AsyncWith,
)


def _max_depth(node: ast.AST, depth: int = 0) -> int:
    best = depth
    for child in ast.iter_child_nodes(node):
        if isinstance(child, _NESTING):
            best = max(best, _max_depth(child, depth + 1))
        else:
            best = max(best, _max_depth(child, depth))
    return best


class ShallowNesting:
    number = NUMBER
    name = NAME
    RuleConfig = RuleConfig

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult:
        depths = []
        violations = []
        for f in iter_functions(codebase):
            d = _max_depth(f.node)
            depths.append(d)
            if d >= config.violation_threshold:
                violations.append(
                    {
                        "file": f.file.relpath,
                        "line": f.lineno,
                        "function": f.qualname or f.name,
                        "depth": d,
                    }
                )

        if not depths:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        p95 = percentile([float(d) for d in depths], 95)
        score = clamp(100 - config.slope * max(0, p95 - config.depth_budget))
        violations.sort(key=lambda v: v["depth"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(p95, 2),
            score_contribution=score,
            status="measured",
            detail={"p95_depth": round(p95, 2), "function_count": len(depths)},
            violations=violations[:50],
        )
