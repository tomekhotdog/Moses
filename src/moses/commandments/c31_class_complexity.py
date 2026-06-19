"""Commandment 31 — Contain class complexity (WMC).

WMC = sum of cyclomatic complexity over a class's methods (radon).
Mean across classes. Curve: 100 at ≤20, → 0 at ≥60 (linear between).
"""

from __future__ import annotations

import ast

from radon.complexity import cc_visit

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_classes, mean, methods_of

NUMBER = 31
NAME = "Contain class complexity"
WMC_FLOOR = 20
WMC_CEIL = 60


def _cc_by_class(source_text: str) -> dict[str, dict[str, int]]:
    """Map class name -> {method name -> cyclomatic complexity}."""
    out: dict[str, dict[str, int]] = {}
    try:
        blocks = cc_visit(source_text)
    except Exception:  # noqa: BLE001 - radon may raise broadly
        return out
    for block in blocks:
        classname = getattr(block, "classname", None)
        if classname is None:
            continue
        out.setdefault(classname, {})[block.name] = block.complexity
    return out


class ClassComplexity:
    number = NUMBER
    name = NAME

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase) -> CommandmentResult:
        values = []
        violations = []
        for source, cls in iter_classes(codebase):
            methods = methods_of(cls)
            if not methods:
                continue
            cc_map = _cc_by_class(source.text).get(cls.name, {})
            wmc = sum(cc_map.get(m.name, 1) for m in methods)
            values.append(wmc)
            if wmc > WMC_FLOOR:
                violations.append(
                    {
                        "file": source.relpath,
                        "line": cls.lineno,
                        "function": cls.name,
                        "wmc": wmc,
                    }
                )

        if not values:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(values)
        if m <= WMC_FLOOR:
            score = 100.0
        elif m >= WMC_CEIL:
            score = 0.0
        else:
            score = 100.0 * (WMC_CEIL - m) / (WMC_CEIL - WMC_FLOOR)
        score = clamp(score)
        violations.sort(key=lambda v: v["wmc"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_wmc": round(m, 2), "class_count": len(values)},
            violations=violations[:50],
        )
