"""Commandment 3 — No pass-through methods.

A pass-through: a function whose body is a single return/expression delegating
to another callable with the same args. Metric: pass_through / total.
Curve: 100 − 1000·M (0 at ≥ 10%).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_functions, param_names

NUMBER = 3
NAME = "No pass-through methods"


@dataclass(frozen=True)
class Params:
    slope: float = 1000.0


def _is_pass_through(node) -> bool:
    body = [s for s in node.body if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))]
    if len(body) != 1:
        return False
    stmt = body[0]
    if isinstance(stmt, ast.Return):
        call = stmt.value
    elif isinstance(stmt, ast.Expr):
        call = stmt.value
    else:
        return False
    if not isinstance(call, ast.Call):
        return False

    # A pass-through delegates to a *method* on another object — `obj.method(...)`
    # or `self.other(...)`. Plain function/builtin calls (e.g. `sum(...)`) are not
    # delegation and never count.
    if not isinstance(call.func, ast.Attribute):
        return False

    # The arguments must be either nothing or simple name forwards. Generators,
    # comprehensions, literals, and computed expressions mean the method is doing
    # real work, not merely forwarding.
    if call.keywords:
        return False
    if not all(isinstance(a, ast.Name) for a in call.args):
        return False

    own_params = set(param_names(node, skip_self=True))
    forwarded = {a.id for a in call.args if isinstance(a, ast.Name)}

    # The receiver (e.g. `obj` in `obj.add_item(...)`) is not a forwarded data arg.
    receiver = None
    if isinstance(call.func.value, ast.Name):
        receiver = call.func.value.id
    data_params = own_params - ({receiver} if receiver else set())

    # A pass-through forwards exactly its data params to the single delegated call.
    # A zero-param method only counts if it forwards nothing AND has no own params.
    if not data_params:
        return not forwarded
    return forwarded == data_params


class PassThrough:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params | None = None) -> CommandmentResult:
        params = params if params is not None else Params()
        total = 0
        violations = []
        for f in iter_functions(codebase):
            total += 1
            if _is_pass_through(f.node):
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
            detail={"pass_through": len(violations), "total": total},
            violations=violations[:50],
        )
