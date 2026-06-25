"""Commandment 12 — Low cognitive complexity.

Composite: 0.7·S_cog + 0.3·S_cyc.
Cognitive = SonarSource definition (custom AST visitor).
Cyclomatic = radon. Each curve: 100 − 10·max(0, mean − 5).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from radon.complexity import cc_visit

from ..models import CommandmentResult
from ._ast_helpers import clamp, iter_functions, mean

NUMBER = 12
NAME = "Low cognitive complexity"


@dataclass(frozen=True)
class Params:
    complexity_budget: int = 5
    slope: float = 10.0
    cog_weight: float = 0.7
    cyc_weight: float = 0.3
    violation_threshold: int = 10

_NESTING_STATEMENTS = (
    ast.If,
    ast.For,
    ast.While,
    ast.Try,
    ast.ExceptHandler,
    ast.With,
    ast.AsyncFor,
    ast.AsyncWith,
)


class _CognitiveVisitor(ast.NodeVisitor):
    """SonarSource cognitive complexity: +1 per break in flow, +nesting penalty."""

    def __init__(self) -> None:
        self.score = 0
        self._nesting = 0

    def _structural(self, node: ast.AST) -> None:
        self.score += 1 + self._nesting
        self._nesting += 1
        self.generic_visit(node)
        self._nesting -= 1

    visit_If = _structural
    visit_For = _structural
    visit_While = _structural
    visit_AsyncFor = _structural
    visit_ExceptHandler = _structural

    def visit_With(self, node: ast.With) -> None:
        # With/AsyncWith add nesting but no flow-break increment.
        self._nesting += 1
        self.generic_visit(node)
        self._nesting -= 1

    visit_AsyncWith = visit_With

    def visit_BoolOp(self, node: ast.BoolOp) -> None:
        # Each sequence of like boolean operators adds 1.
        self.score += 1
        self.generic_visit(node)

    def visit_Break(self, node: ast.Break) -> None:
        self.score += 1

    def visit_Continue(self, node: ast.Continue) -> None:
        self.score += 1

    def _nested_function(self, node) -> None:
        self._nesting += 1
        self.generic_visit(node)
        self._nesting -= 1

    visit_FunctionDef = _nested_function
    visit_AsyncFunctionDef = _nested_function


def cognitive_complexity(node) -> int:
    visitor = _CognitiveVisitor()
    for child in ast.iter_child_nodes(node):
        visitor.visit(child)
    return visitor.score


def _cyclomatic_by_name(source_text: str) -> dict[str, int]:
    result: dict[str, int] = {}
    try:
        for block in cc_visit(source_text):
            result[block.name] = block.complexity
            full = f"{getattr(block, 'classname', None)}.{block.name}" if getattr(
                block, "classname", None
            ) else block.name
            result[full] = block.complexity
    except (SyntaxError, Exception):  # noqa: BLE001 - radon can raise broadly
        pass
    return result


class LowCognitiveComplexity:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params | None = None) -> CommandmentResult:
        params = params if params is not None else Params()
        cog_values: list[int] = []
        cyc_values: list[int] = []
        violations = []

        cyc_cache: dict[str, dict[str, int]] = {}
        for f in iter_functions(codebase):
            cog = cognitive_complexity(f.node)
            cog_values.append(cog)

            if f.file.relpath not in cyc_cache:
                cyc_cache[f.file.relpath] = _cyclomatic_by_name(f.file.text)
            cyc_map = cyc_cache[f.file.relpath]
            cyc = cyc_map.get(f.qualname) or cyc_map.get(f.name) or 1
            cyc_values.append(cyc)

            if cog >= params.violation_threshold or cyc >= params.violation_threshold:
                violations.append(
                    {
                        "file": f.file.relpath,
                        "line": f.lineno,
                        "function": f.qualname or f.name,
                        "cognitive": cog,
                        "cyclomatic": cyc,
                    }
                )

        if not cog_values:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        mean_cog = mean(cog_values)
        mean_cyc = mean(cyc_values)
        s_cog = clamp(100 - params.slope * max(0, mean_cog - params.complexity_budget))
        s_cyc = clamp(100 - params.slope * max(0, mean_cyc - params.complexity_budget))
        score = clamp(params.cog_weight * s_cog + params.cyc_weight * s_cyc)

        violations.sort(key=lambda v: v["cognitive"] + v["cyclomatic"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(mean_cog, 2),
            score_contribution=score,
            status="measured",
            detail={
                "mean_cognitive": round(mean_cog, 2),
                "mean_cyclomatic": round(mean_cyc, 2),
                "s_cog": round(s_cog, 2),
                "s_cyc": round(s_cyc, 2),
            },
            violations=violations[:50],
        )
