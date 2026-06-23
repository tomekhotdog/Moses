"""Commandment 27 — Data over primitives (Domain Surface Ratio).

Score each public, annotated type slot (parameter, return, class attribute) on a
domain-richness scale: a Concept (class/NewType/Enum/dataclass/value type) = 1.0,
a weak type (Literal) = 0.5, a Primitive (str/int/.../Any/bare container) = 0.0.
Containers score by their type arguments: list[X] -> score(X); dict[K, V] ->
min(score(K), score(V)); Optional[X] -> score(X). The Metric is the mean across
qualifying slots — the Domain Surface Ratio. Curve: 100 * DSR / TARGET_RATIO.
"""

from __future__ import annotations

import ast

NUMBER = 27
NAME = "Data over primitives"

PRIMITIVE_NAMES = frozenset(
    {"str", "int", "float", "bool", "bytes", "complex", "bytearray", "object", "Any", "None", "NoneType"}
)
BARE_CONTAINER_NAMES = frozenset(
    {"dict", "list", "tuple", "set", "frozenset", "Dict", "List", "Tuple", "Set", "FrozenSet"}
)
SEQUENCE_CONTAINERS = frozenset(
    {"list", "set", "frozenset", "Sequence", "Iterable", "Collection", "MutableSequence",
     "AbstractSet", "Iterator", "List", "Set", "FrozenSet"}
)
MAPPING_CONTAINERS = frozenset(
    {"dict", "Mapping", "MutableMapping", "DefaultDict", "OrderedDict", "Dict"}
)
TUPLE_CONTAINERS = frozenset({"tuple", "Tuple"})


def _is_none(node: ast.expr) -> bool:
    return isinstance(node, ast.Constant) and node.value is None


def _flatten_union(node: ast.expr) -> list[ast.expr]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return _flatten_union(node.left) + _flatten_union(node.right)
    return [node]


def _container_name(value: ast.expr) -> str | None:
    if isinstance(value, ast.Name):
        return value.id
    if isinstance(value, ast.Attribute):
        return value.attr
    return None


def _slice_args(node: ast.Subscript) -> list[ast.expr]:
    s = node.slice
    if isinstance(s, ast.Tuple):
        return list(s.elts)
    return [s]


def _classify_subscript(node: ast.Subscript) -> float:
    name = _container_name(node.value)
    if name is None:
        return 1.0
    args = _slice_args(node)
    if name == "Optional":
        return classify_annotation(args[0]) if args else 0.0
    if name == "Union":
        members = [a for a in args if not _is_none(a)]
        return min((classify_annotation(m) for m in members), default=0.0)
    if name == "Literal":
        return 0.5
    if name in SEQUENCE_CONTAINERS:
        return classify_annotation(args[0]) if args else 0.0
    if name in MAPPING_CONTAINERS:
        if len(args) >= 2:
            return min(classify_annotation(args[0]), classify_annotation(args[1]))
        return 0.0
    if name in TUPLE_CONTAINERS:
        real = [a for a in args if not (isinstance(a, ast.Constant) and a.value is Ellipsis)]
        return min((classify_annotation(a) for a in real), default=0.0)
    if name in PRIMITIVE_NAMES:
        return 0.0
    return 1.0  # an unrecognised generic like Result[Order] is a concept


def classify_annotation(node: ast.expr | None) -> float:
    """Domain-richness of one annotation in [0, 1]; None means 'unannotated' -> 0."""
    if node is None:
        return 0.0
    if isinstance(node, ast.Constant):
        if node.value is None:
            return 0.0
        if isinstance(node.value, str):  # forward ref, e.g. x: "Order"
            return 0.0 if node.value in PRIMITIVE_NAMES else 1.0
        return 0.0
    if isinstance(node, ast.Name):
        if node.id in PRIMITIVE_NAMES or node.id in BARE_CONTAINER_NAMES:
            return 0.0
        return 1.0
    if isinstance(node, ast.Attribute):
        return 0.0 if node.attr in PRIMITIVE_NAMES else 1.0
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        members = [m for m in _flatten_union(node) if not _is_none(m)]
        return min((classify_annotation(m) for m in members), default=0.0)
    if isinstance(node, ast.Subscript):
        return _classify_subscript(node)
    return 1.0
