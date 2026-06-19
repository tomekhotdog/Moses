"""Shared AST primitives. Commandment files import only from here + models.

The only shared toolkit: parse_file, iter_functions, FunctionInfo, plus the
small numeric helpers clamp/mean/percentile.
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from typing import Iterable, Iterator

from ..models import Codebase, SourceFile

FunctionNode = ast.FunctionDef | ast.AsyncFunctionDef

_UNSET = object()


def parse_file(source: SourceFile) -> ast.Module | None:
    """Parse a SourceFile into a module AST, or None on SyntaxError.

    Memoised on the SourceFile instance to avoid re-parsing within a run,
    without a process-global cache that could leak across runs or reuse ids.
    """
    cached = getattr(source, "_moses_ast", _UNSET)
    if cached is not _UNSET:
        return cached
    try:
        tree = ast.parse(source.text, filename=str(source.path))
    except (SyntaxError, ValueError):
        tree = None
    source._moses_ast = tree  # type: ignore[attr-defined]
    return tree


@dataclass
class FunctionInfo:
    """A function/method discovered in the Codebase."""

    file: SourceFile
    node: FunctionNode
    name: str
    non_blank_loc: int
    qualname: str = ""

    @property
    def lineno(self) -> int:
        return self.node.lineno

    @property
    def is_method(self) -> bool:
        return "." in self.qualname


def _node_non_blank_loc(node: FunctionNode, source: SourceFile) -> int:
    start = node.lineno
    end = getattr(node, "end_lineno", node.lineno) or node.lineno
    lines = source.text.splitlines()[start - 1 : end]
    return sum(1 for line in lines if line.strip())


def iter_functions(codebase: Codebase) -> Iterator[FunctionInfo]:
    """Yield every function and method in the Codebase."""
    for source in codebase.files:
        tree = parse_file(source)
        if tree is None:
            continue
        yield from _iter_functions_in_tree(tree, source)


def _iter_functions_in_tree(tree: ast.Module, source: SourceFile) -> Iterator[FunctionInfo]:
    def walk(node: ast.AST, prefix: str) -> Iterator[FunctionInfo]:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                qual = f"{prefix}{child.name}" if prefix else child.name
                yield FunctionInfo(
                    file=source,
                    node=child,
                    name=child.name,
                    non_blank_loc=_node_non_blank_loc(child, source),
                    qualname=qual,
                )
                yield from walk(child, f"{qual}.")
            elif isinstance(child, ast.ClassDef):
                yield from walk(child, f"{prefix}{child.name}.")
            else:
                yield from walk(child, prefix)

    yield from walk(tree, "")


def iter_classes(codebase: Codebase) -> Iterator[tuple[SourceFile, ast.ClassDef]]:
    """Yield (file, ClassDef) for every class in the Codebase."""
    for source in codebase.files:
        tree = parse_file(source)
        if tree is None:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                yield source, node


def methods_of(cls: ast.ClassDef) -> list[FunctionNode]:
    return [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]


def is_dunder(name: str) -> bool:
    return name.startswith("__") and name.endswith("__")


def is_private(name: str) -> bool:
    return name.startswith("_") and not is_dunder(name)


def param_names(node: FunctionNode, *, skip_self: bool = True) -> list[str]:
    """Positional + keyword-only param names, optionally skipping self/cls."""
    args = node.args
    names = [a.arg for a in args.posonlyargs]
    names += [a.arg for a in args.args]
    names += [a.arg for a in args.kwonlyargs]
    if args.vararg:
        names.append(args.vararg.arg)
    if args.kwarg:
        names.append(args.kwarg.arg)
    if skip_self and names and names[0] in ("self", "cls"):
        names = names[1:]
    return names


def required_param_count(node: FunctionNode, *, skip_self: bool = True) -> int:
    """Count params with no default value (excluding *args/**kwargs)."""
    args = node.args
    positional = list(args.posonlyargs) + list(args.args)
    n_defaults = len(args.defaults)
    required_positional = positional[: len(positional) - n_defaults]
    if skip_self and required_positional and required_positional[0].arg in ("self", "cls"):
        required_positional = required_positional[1:]
    required_kwonly = sum(1 for d in args.kw_defaults if d is None)
    return len(required_positional) + required_kwonly


def clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def mean(values: Iterable[float]) -> float:
    values = list(values)
    if not values:
        return 0.0
    return sum(values) / len(values)


def percentile(values: list[float], q: float) -> float:
    """Linear-interpolation percentile; ``q`` in [0, 100]."""
    if not values:
        return 0.0
    ordered = sorted(values)
    if len(ordered) == 1:
        return float(ordered[0])
    rank = (q / 100.0) * (len(ordered) - 1)
    low = int(rank)
    high = min(low + 1, len(ordered) - 1)
    frac = rank - low
    return ordered[low] * (1 - frac) + ordered[high] * frac
