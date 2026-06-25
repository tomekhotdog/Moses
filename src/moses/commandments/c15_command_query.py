"""Commandment 15 — Command–query separation.

A violator: a function that returns non-None *and* mutates non-local state
(assignment to attribute / subscript / nonlocal / global).
Metric: violators / total. Curve: 100 − 500·M.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_functions

NUMBER = 15
NAME = "Command-query separation"


@dataclass(frozen=True)
class Params:
    slope: float = 500.0


def _returns_value(node) -> bool:
    for child in ast.walk(node):
        if isinstance(child, ast.Return) and child.value is not None:
            # Ignore `return None` literal.
            if isinstance(child.value, ast.Constant) and child.value.value is None:
                continue
            return True
    return False


def _mutates_nonlocal_state(node) -> bool:
    for child in ast.walk(node):
        if isinstance(child, (ast.Global, ast.Nonlocal)):
            return True
        if isinstance(child, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
            targets = child.targets if isinstance(child, ast.Assign) else [child.target]
            for tgt in targets:
                if isinstance(tgt, (ast.Attribute, ast.Subscript)):
                    return True
    return False


class CommandQuery:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params) -> CommandmentResult:
        total = 0
        violations = []
        for f in iter_functions(codebase):
            total += 1
            if _returns_value(f.node) and _mutates_nonlocal_state(f.node):
                violations.append(
                    {
                        "file": f.file.relpath,
                        "line": f.lineno,
                        "function": f.qualname or f.name,
                    }
                )

        if total == 0:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = len(violations) / total
        score = clamp(100 - params.slope * m)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 3),
            score_contribution=score,
            status="measured",
            detail={"violators": len(violations), "total": total},
            violations=violations[:50],
        )
