"""Commandment 23 — Narrow variable scope.

Per local var: (last_use_line − first_assign_line) / function_LOC. Mean.
Curve: 100 − 200·max(0, M − 0.3).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_functions, mean

NUMBER = 23
NAME = "Narrow variable scope"


@dataclass(frozen=True)
class Params:
    scope_budget: float = 0.3
    slope: float = 200.0


def _local_live_ranges(node) -> dict[str, tuple[int, int]]:
    """For each assigned local, (first_assign_line, last_use_line)."""
    first_assign: dict[str, int] = {}
    last_use: dict[str, int] = {}

    for child in ast.walk(node):
        if isinstance(child, ast.Name):
            line = getattr(child, "lineno", None)
            if line is None:
                continue
            if isinstance(child.ctx, ast.Store):
                if child.id not in first_assign:
                    first_assign[child.id] = line
                last_use[child.id] = max(last_use.get(child.id, line), line)
            elif isinstance(child.ctx, ast.Load):
                if child.id in first_assign:
                    last_use[child.id] = max(last_use.get(child.id, line), line)

    return {
        name: (first_assign[name], last_use.get(name, first_assign[name]))
        for name in first_assign
    }


class NarrowScope:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params) -> CommandmentResult:
        ratios = []
        violations = []
        for f in iter_functions(codebase):
            func_loc = max(1, f.non_blank_loc)
            ranges = _local_live_ranges(f.node)
            for var, (first, last) in ranges.items():
                ratio = (last - first) / func_loc
                ratios.append(ratio)
                if ratio > 0.5:
                    violations.append(
                        {
                            "file": f.file.relpath,
                            "line": first,
                            "function": f.qualname or f.name,
                            "variable": var,
                            "scope_ratio": round(ratio, 2),
                        }
                    )

        if not ratios:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(ratios)
        score = clamp(100 - params.slope * max(0, m - params.scope_budget))
        violations.sort(key=lambda v: v["scope_ratio"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 3),
            score_contribution=score,
            status="measured",
            detail={"mean_scope_ratio": round(m, 3), "local_count": len(ratios)},
            violations=violations[:50],
        )
