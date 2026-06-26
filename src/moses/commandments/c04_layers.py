"""Commandment 4 — Layers add abstraction.

Detects delegation-wrapper classes: a class that stores an injected object and
forwards >= min_forwarders public methods to it BY THE SAME NAME (>= forward_fraction
of its public methods) — a layer that adds no abstraction over the wrapped object.
Same-name requirement spares genuine Adapters/Facades that transform the interface.
Metric: wrapper classes / total classes. Curve: 100 - slope*ratio.
"""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_dunder, is_private, iter_classes, methods_of

NUMBER = 4
NAME = "Layers add abstraction"


@dataclass(frozen=True)
class RuleConfig:
    slope: float = 200.0
    min_forwarders: int = 3
    forward_fraction: float = 0.6


def _self_name(method) -> str | None:
    args = method.args.args
    return args[0].arg if args else None


def _wrapped_attrs(cls: ast.ClassDef) -> set[str]:
    """self.<attr> names assigned directly from an __init__ parameter."""
    attrs: set[str] = set()
    for m in methods_of(cls):
        if m.name != "__init__":
            continue
        params = {a.arg for a in m.args.args}
        self_name = _self_name(m)
        for node in ast.walk(m):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                tgt = node.targets[0]
                if (
                    isinstance(tgt, ast.Attribute)
                    and isinstance(tgt.value, ast.Name)
                    and tgt.value.id == self_name
                    and isinstance(node.value, ast.Name)
                    and node.value.id in params
                ):
                    attrs.add(tgt.attr)
    return attrs


def _forwards_to(method, self_name: str | None) -> str | None:
    """If body is a single `self.<attr>.<same name>(...)`, return <attr>, else None."""
    body = [
        s
        for s in method.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
    ]
    if len(body) != 1:
        return None
    stmt = body[0]
    call = stmt.value if isinstance(stmt, (ast.Return, ast.Expr)) else None
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
        return None
    if call.func.attr != method.name:  # same-name forwarding only
        return None
    inner = call.func.value
    if isinstance(inner, ast.Attribute) and isinstance(inner.value, ast.Name) and inner.value.id == self_name:
        return inner.attr
    return None


def _is_delegation_wrapper(cls: ast.ClassDef, config: RuleConfig) -> bool:
    wrapped = _wrapped_attrs(cls)
    if not wrapped:
        return False
    public = [m for m in methods_of(cls) if not is_dunder(m.name) and not is_private(m.name)]
    if not public:
        return False
    fwd: Counter = Counter()
    for m in public:
        attr = _forwards_to(m, _self_name(m))
        if attr in wrapped:
            fwd[attr] += 1
    if not fwd:
        return False
    best = max(fwd.values())
    return best >= config.min_forwarders and best / len(public) >= config.forward_fraction


class Layers:
    number = NUMBER
    name = NAME
    RuleConfig = RuleConfig

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult:
        total = 0
        violations = []
        for source, cls in iter_classes(codebase):
            total += 1
            if _is_delegation_wrapper(cls, config):
                violations.append(
                    {"file": source.relpath, "line": cls.lineno, "function": cls.name}
                )

        if total == 0:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = len(violations) / total
        score = clamp(100 - config.slope * m)
        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 3),
            score_contribution=score,
            status="measured",
            detail={"wrappers": len(violations), "class_count": total},
            violations=violations[:50],
        )
