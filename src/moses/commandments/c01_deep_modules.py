"""Commandment 1 — Deep modules.

Per file: impl_LOC / API_surface, where API_surface = Σ(1 + param_count) over
public funcs/methods (skip self/cls, treat _-prefixed as private, dunders count).
Average across files. Curve: 10·M, saturates at 10 (i.e. score 100 at M ≥ 10).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_private, mean, param_names, parse_file

NUMBER = 1
NAME = "Deep modules"


@dataclass(frozen=True)
class Params:
    multiplier: float = 10.0


def _api_surface_and_impl(tree: ast.Module, source) -> tuple[float, int]:
    surface = 0.0
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if is_private(node.name):
                continue
            params = param_names(node, skip_self=True)
            surface += 1 + len(params)
    impl = source.non_blank_loc
    return surface, impl


class DeepModules:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params | None = None) -> CommandmentResult:
        params = params if params is not None else Params()
        depths = []
        violations = []
        for source in codebase.files:
            tree = parse_file(source)
            if tree is None:
                continue
            surface, impl = _api_surface_and_impl(tree, source)
            if surface <= 0:
                continue
            depth = impl / surface
            depths.append(depth)
            if depth < 3:
                violations.append(
                    {
                        "file": source.relpath,
                        "line": 1,
                        "function": "<module>",
                        "depth": round(depth, 2),
                    }
                )

        if not depths:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(depths)
        score = clamp(params.multiplier * m)
        violations.sort(key=lambda v: v["depth"])

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_depth": round(m, 2), "file_count": len(depths)},
            violations=violations[:50],
        )
