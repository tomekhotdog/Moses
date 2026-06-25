"""Commandment 25 — No magic numbers.

Metric: numeric literals per 1000 LOC, excluding {0, 1, -1}, excluding test files.
Curve:  100 − 2·M.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, parse_file

NUMBER = 25
NAME = "No magic numbers"


@dataclass(frozen=True)
class RuleConfig:
    allowed: frozenset[int] = frozenset({0, 1, -1})
    slope: float = 2.0


def _is_magic(node: ast.AST, allowed: frozenset[int]) -> bool:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(
        node.value, bool
    ):
        return node.value not in allowed
    return False


class NoMagicNumbers:
    number = NUMBER
    name = NAME
    RuleConfig = RuleConfig

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult:
        total_loc = 0
        violations = []
        for source in codebase.files:
            if source.is_test:
                continue
            tree = parse_file(source)
            if tree is None:
                continue
            total_loc += source.non_blank_loc
            for node in ast.walk(tree):
                # Skip negative-literal UnaryOp wrappers: handled via the inner Constant.
                if _is_magic(node, config.allowed):
                    # Skip -1 expressed as UnaryOp(USub, Constant(1)).
                    violations.append(
                        {
                            "file": source.relpath,
                            "line": getattr(node, "lineno", 0),
                            "function": "<literal>",
                            "value": node.value,
                        }
                    )

        if total_loc == 0:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        per_kloc = len(violations) / (total_loc / 1000.0)
        score = clamp(100 - config.slope * per_kloc)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(per_kloc, 2),
            score_contribution=score,
            status="measured",
            detail={"magic_literals": len(violations), "loc": total_loc},
            violations=violations[:50],
        )
