"""Commandment 18 — No empty catch blocks.

Metric: `except: pass` or `except: ...` (Constant Ellipsis) per 1000 LOC.
Curve:  100 − 100·M.
"""

from __future__ import annotations

import ast

from ..models import CommandmentResult
from ._ast_helpers import clamp, parse_file

NUMBER = 18
NAME = "No empty catch blocks"


def _is_empty_handler(handler: ast.ExceptHandler) -> bool:
    body = handler.body
    if len(body) != 1:
        return False
    stmt = body[0]
    if isinstance(stmt, ast.Pass):
        return True
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
        return stmt.value.value is Ellipsis
    return False


class NoEmptyCatch:
    number = NUMBER
    name = NAME

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase) -> CommandmentResult:
        total_loc = 0
        violations = []
        for source in codebase.files:
            tree = parse_file(source)
            if tree is None:
                continue
            total_loc += source.non_blank_loc
            for node in ast.walk(tree):
                if isinstance(node, ast.ExceptHandler) and _is_empty_handler(node):
                    violations.append(
                        {
                            "file": source.relpath,
                            "line": node.lineno,
                            "function": "<except>",
                        }
                    )

        if total_loc == 0:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        per_kloc = len(violations) / (total_loc / 1000.0)
        score = clamp(100 - 100 * per_kloc)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(per_kloc, 3),
            score_contribution=score,
            status="measured",
            detail={"empty_handlers": len(violations), "loc": total_loc},
            violations=violations[:50],
        )
