"""Commandment 29 — Composition over inheritance.

Metric: mean inheritance depth, excluding stdlib/third-party bases (any base
whose name isn't defined in this codebase). Curve: 100 − 50·max(0, M − 1).
"""

from __future__ import annotations

import ast

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_classes, mean

NUMBER = 29
NAME = "Composition over inheritance"


def _base_names(cls: ast.ClassDef) -> list[str]:
    names = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


class Composition:
    number = NUMBER
    name = NAME

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase) -> CommandmentResult:
        classes: dict[str, ast.ClassDef] = {}
        located: dict[str, str] = {}
        for source, cls in iter_classes(codebase):
            classes[cls.name] = cls
            located[cls.name] = source.relpath

        if not classes:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        depth_cache: dict[str, int] = {}

        def depth(name: str, seen: frozenset[str]) -> int:
            if name in depth_cache:
                return depth_cache[name]
            if name not in classes or name in seen:
                return 0
            cls = classes[name]
            local_bases = [b for b in _base_names(cls) if b in classes]
            if not local_bases:
                depth_cache[name] = 0
                return 0
            best = 1 + max(depth(b, seen | {name}) for b in local_bases)
            depth_cache[name] = best
            return best

        values = []
        violations = []
        for name, cls in classes.items():
            d = depth(name, frozenset())
            values.append(d)
            if d > 1:
                violations.append(
                    {
                        "file": located[name],
                        "line": cls.lineno,
                        "function": name,
                        "depth": d,
                    }
                )

        m = mean(values)
        score = clamp(100 - 50 * max(0, m - 1))
        violations.sort(key=lambda v: v["depth"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_depth": round(m, 2), "class_count": len(values)},
            violations=violations[:50],
        )
