"""Commandment 21 — Cohesive classes (LCOM4).

Build an undirected graph over a class's methods: edge if two methods share an
instance attribute or one calls the other. LCOM4 = number of connected
components. Mean across classes. Curve: 100 − 50·max(0, M − 1).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_dunder, iter_classes, mean, methods_of

NUMBER = 21
NAME = "Cohesive classes"


@dataclass(frozen=True)
class Params:
    budget: float = 1.0
    slope: float = 50.0


def _self_attrs(method) -> set[str]:
    attrs: set[str] = set()
    self_name = method.args.args[0].arg if method.args.args else None
    if self_name is None:
        return attrs
    for node in ast.walk(method):
        if (
            isinstance(node, ast.Attribute)
            and isinstance(node.value, ast.Name)
            and node.value.id == self_name
        ):
            attrs.add(node.attr)
    return attrs


def _calls_to_self_methods(method) -> set[str]:
    calls: set[str] = set()
    self_name = method.args.args[0].arg if method.args.args else None
    if self_name is None:
        return calls
    for node in ast.walk(method):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == self_name
        ):
            calls.add(node.func.attr)
    return calls


def lcom4(cls: ast.ClassDef) -> int:
    methods = [m for m in methods_of(cls) if not is_dunder(m.name)]
    names = [m.name for m in methods]
    if len(methods) <= 1:
        return 1 if methods else 0

    attrs = {m.name: _self_attrs(m) for m in methods}
    calls = {m.name: _calls_to_self_methods(m) for m in methods}
    name_set = set(names)

    parent = {n: n for n in names}

    def find(x: str) -> str:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: str, b: str) -> None:
        parent[find(a)] = find(b)

    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            shares_attr = bool(attrs[a] & attrs[b])
            calls_each = (b in calls[a]) or (a in calls[b])
            if shares_attr or calls_each:
                union(a, b)
        # method that calls another self method links them.
        for callee in calls[a] & name_set:
            union(a, callee)

    components = {find(n) for n in names}
    return len(components)


class CohesiveClasses:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params) -> CommandmentResult:
        values = []
        violations = []
        for source, cls in iter_classes(codebase):
            score = lcom4(cls)
            if score == 0:
                continue
            values.append(score)
            if score > 1:
                violations.append(
                    {
                        "file": source.relpath,
                        "line": cls.lineno,
                        "function": cls.name,
                        "lcom4": score,
                    }
                )

        if not values:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(values)
        score = clamp(100 - params.slope * max(0, m - params.budget))
        violations.sort(key=lambda v: v["lcom4"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_lcom4": round(m, 2), "class_count": len(values)},
            violations=violations[:50],
        )
