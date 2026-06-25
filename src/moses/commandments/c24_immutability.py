"""Commandment 24 — Prefer immutability.

Metric: fraction of locals reassigned after first binding (excludes
augmented-assign-only cases via simple dataflow). Curve: 100 − 200·M.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_functions

NUMBER = 24
NAME = "Prefer immutability"


@dataclass(frozen=True)
class Params:
    slope: float = 200.0


def _reassignment_stats(node) -> tuple[int, int, list[str]]:
    """Return (total_locals, reassigned_locals, reassigned_names).

    A plain reassignment is a second-or-later ast.Assign Store to a name that
    was previously plainly assigned. Augmented assignments alone don't count.
    """
    plain_assigns: dict[str, int] = {}
    aug_only: set[str] = set()

    for child in ast.walk(node):
        if isinstance(child, ast.Assign):
            for tgt in child.targets:
                for name in _names_in_target(tgt):
                    plain_assigns[name] = plain_assigns.get(name, 0) + 1
        elif isinstance(child, ast.AugAssign):
            if isinstance(child.target, ast.Name):
                aug_only.add(child.target.id)

    reassigned = [n for n, c in plain_assigns.items() if c > 1]
    total = len(plain_assigns)
    return total, len(reassigned), reassigned


def _names_in_target(tgt: ast.AST) -> list[str]:
    if isinstance(tgt, ast.Name):
        return [tgt.id]
    names = []
    if isinstance(tgt, (ast.Tuple, ast.List)):
        for el in tgt.elts:
            names.extend(_names_in_target(el))
    return names


class Immutability:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params) -> CommandmentResult:
        total_locals = 0
        total_reassigned = 0
        violations = []
        for f in iter_functions(codebase):
            total, reassigned, names = _reassignment_stats(f.node)
            total_locals += total
            total_reassigned += reassigned
            if reassigned:
                violations.append(
                    {
                        "file": f.file.relpath,
                        "line": f.lineno,
                        "function": f.qualname or f.name,
                        "reassigned": names,
                        "count": reassigned,
                    }
                )

        if total_locals == 0:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = total_reassigned / total_locals
        score = clamp(100 - params.slope * m)
        violations.sort(key=lambda v: v["count"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 3),
            score_contribution=score,
            status="measured",
            detail={
                "reassigned_locals": total_reassigned,
                "total_locals": total_locals,
            },
            violations=violations[:50],
        )
