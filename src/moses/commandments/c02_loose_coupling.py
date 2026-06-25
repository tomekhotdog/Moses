"""Commandment 2 — Loose coupling (CBO).

Per class: count distinct *imported* names referenced inside the class body.
Mean across classes. Curve: 100 at M ≤ 14, → 0 at M ≥ 20 (linear between).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_classes, mean, parse_file

NUMBER = 2
NAME = "Loose coupling"


@dataclass(frozen=True)
class Params:
    floor: float = 14.0
    ceil: float = 20.0


def _imported_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


def _referenced_imports(cls: ast.ClassDef, imports: set[str]) -> set[str]:
    used: set[str] = set()
    for node in ast.walk(cls):
        if isinstance(node, ast.Name) and node.id in imports:
            used.add(node.id)
        elif isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
            if node.value.id in imports:
                used.add(node.value.id)
    return used


class LooseCoupling:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params) -> CommandmentResult:
        cbos = []
        violations = []
        imports_by_file: dict[str, set[str]] = {}
        for source in codebase.files:
            tree = parse_file(source)
            if tree is None:
                continue
            imports_by_file[source.relpath] = _imported_names(tree)

        for source, cls in iter_classes(codebase):
            imports = imports_by_file.get(source.relpath, set())
            cbo = len(_referenced_imports(cls, imports))
            cbos.append(cbo)
            if cbo > params.floor:
                violations.append(
                    {
                        "file": source.relpath,
                        "line": cls.lineno,
                        "function": cls.name,
                        "cbo": cbo,
                    }
                )

        if not cbos:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(cbos)
        if m <= params.floor:
            score = 100.0
        elif m >= params.ceil:
            score = 0.0
        else:
            score = 100.0 * (params.ceil - m) / (params.ceil - params.floor)
        score = clamp(score)
        violations.sort(key=lambda v: v["cbo"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_cbo": round(m, 2), "class_count": len(cbos)},
            violations=violations[:50],
        )
