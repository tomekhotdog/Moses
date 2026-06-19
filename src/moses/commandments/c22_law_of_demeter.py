"""Commandment 22 — Law of Demeter.

Metric: mean intermediate-attribute depth at call sites rooted on a Name.
Skip module imports, pathlib idioms, and fluent builders
(with_/set_/add_/build/configure/copy/clone). Curve: 100 − 50·max(0, M − 1).
"""

from __future__ import annotations

import ast

from ..models import CommandmentResult
from ._ast_helpers import clamp, mean, parse_file

NUMBER = 22
NAME = "Law of Demeter"

_FLUENT_PREFIXES = ("with_", "set_", "add_")
_FLUENT_NAMES = {"build", "configure", "copy", "clone"}


def _is_fluent(attr: str) -> bool:
    return attr.startswith(_FLUENT_PREFIXES) or attr in _FLUENT_NAMES


def _chain_depth(call: ast.Call, imports: set[str]) -> int | None:
    """Count intermediate attribute hops for a call rooted on a Name.

    e.g. a.b.c.d() -> attribute chain b,c,d; the call target is the last attr,
    intermediates are b,c -> depth 2. Returns None if not Name-rooted or skipped.
    """
    func = call.func
    if not isinstance(func, ast.Attribute):
        return None
    attrs: list[str] = []
    node: ast.AST = func
    while isinstance(node, ast.Attribute):
        attrs.append(node.attr)
        node = node.value
    if not isinstance(node, ast.Name):
        return None
    root = node.id
    if root in imports:
        return None
    # attrs is reversed: [final_call_attr, ..., first_attr]
    # intermediate hops = number of attribute accesses before the final call
    intermediates = attrs[1:]  # drop the called method itself
    if not intermediates:
        return 0
    if any(_is_fluent(a) for a in attrs):
        return None
    if root in ("self", "cls"):
        # one hop on self is fine; deeper chains still count.
        intermediates = attrs[1:]
    return len(intermediates)


def _collect_imports(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
    return names


class LawOfDemeter:
    number = NUMBER
    name = NAME

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase) -> CommandmentResult:
        depths = []
        violations = []
        for source in codebase.files:
            tree = parse_file(source)
            if tree is None:
                continue
            imports = _collect_imports(tree)
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    depth = _chain_depth(node, imports)
                    if depth is None:
                        continue
                    depths.append(depth)
                    if depth >= 2:
                        violations.append(
                            {
                                "file": source.relpath,
                                "line": getattr(node, "lineno", 0),
                                "function": "<call>",
                                "depth": depth,
                            }
                        )

        if not depths:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(depths)
        score = clamp(100 - 50 * max(0, m - 1))
        violations.sort(key=lambda v: v["depth"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_chain_depth": round(m, 2), "call_sites": len(depths)},
            violations=violations[:50],
        )
