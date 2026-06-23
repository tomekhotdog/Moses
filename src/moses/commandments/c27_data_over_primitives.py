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
TRANSPARENT_WRAPPERS = frozenset(
    {"Annotated", "Final", "ClassVar", "Required", "NotRequired", "ReadOnly"}
)


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
    if name in TRANSPARENT_WRAPPERS:
        # Annotated[T, ...]/Final[T]/ClassVar[T] are transparent: score by T.
        return classify_annotation(args[0]) if args else 0.0
    if name == "Callable":
        # Score a callable by its return type (last arg); params are contravariant.
        return classify_annotation(args[-1]) if args else 1.0
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
            if node.value in PRIMITIVE_NAMES or node.value in BARE_CONTAINER_NAMES:
                return 0.0
            return 1.0
        return 0.0
    if isinstance(node, ast.Name):
        if (
            node.id in PRIMITIVE_NAMES
            or node.id in BARE_CONTAINER_NAMES
            or node.id in SEQUENCE_CONTAINERS
            or node.id in MAPPING_CONTAINERS
            or node.id in TUPLE_CONTAINERS
        ):
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


from ..models import CommandmentResult  # noqa: E402  (kept near rule for locality)
from ._ast_helpers import clamp, is_dunder, is_private, iter_classes, iter_functions, mean, parse_file  # noqa: E402

TARGET_RATIO = 0.6  # DSR earning full marks (opinionated, calibration-pending)
VIOLATION_THRESHOLD = 0.5  # functions whose mean slot score is below this are flagged
PREDICATE_PREFIXES = ("is_", "has_", "can_", "should_", "was_", "are_")
COUNT_NAMES = frozenset({"count", "size", "length", "len", "index", "n", "num", "total"})


def _is_property_or_setter(node) -> bool:
    for dec in node.decorator_list:
        if isinstance(dec, ast.Name) and dec.id == "property":
            return True
        if isinstance(dec, ast.Attribute) and dec.attr in ("setter", "getter", "deleter"):
            return True
    return False


def _param_annotations(node) -> list:
    args = node.args
    all_args = list(args.posonlyargs) + list(args.args) + list(args.kwonlyargs)
    if all_args and all_args[0].arg in ("self", "cls"):
        all_args = all_args[1:]
    return [a.annotation for a in all_args]


def _exempt_return(name: str, ret) -> bool:
    if not isinstance(ret, ast.Name):
        return False
    if ret.id == "bool" and name.startswith(PREDICATE_PREFIXES):
        return True
    if ret.id == "int" and (name in COUNT_NAMES or name.startswith(("count_", "num_"))):
        return True
    return False


def _domain_vocab_density(codebase) -> float:
    defs = 0
    for source in codebase.files:
        if source.is_test:
            continue
        tree = parse_file(source)
        if tree is None:
            continue
        for n in ast.walk(tree):
            if isinstance(n, ast.ClassDef):
                defs += 1
            elif isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                fn = n.value.func
                fn_name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", "")
                if fn_name in ("NewType", "NamedTuple"):
                    defs += 1
    nbloc = codebase.non_blank_loc
    return round(defs / (nbloc / 1000.0), 2) if nbloc else 0.0


class DataOverPrimitives:
    number = NUMBER
    name = NAME

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase) -> CommandmentResult:
        slot_scores: list[float] = []
        annotated = 0
        total_surface = 0
        violations: list[dict] = []

        for f in iter_functions(codebase):
            if f.file.is_test or is_dunder(f.name) or is_private(f.name):
                continue
            if _is_property_or_setter(f.node):
                continue
            fn_scores: list[float] = []
            worst_ann, worst_score = None, 2.0
            for ann in _param_annotations(f.node):
                total_surface += 1
                if ann is None:
                    continue
                annotated += 1
                s = classify_annotation(ann)
                slot_scores.append(s)
                fn_scores.append(s)
                if s < worst_score:
                    worst_score, worst_ann = s, ann
            ret = f.node.returns
            # On ties the return slot wins: it is the most informative signal of a
            # primitive-leaking surface ("what does this hand back?").
            if not _exempt_return(f.name, ret):
                total_surface += 1
                if ret is not None:
                    annotated += 1
                    s = classify_annotation(ret)
                    slot_scores.append(s)
                    fn_scores.append(s)
                    if s <= worst_score:
                        worst_score, worst_ann = s, ret
            if fn_scores:
                fm = mean(fn_scores)
                if fm < VIOLATION_THRESHOLD:
                    violations.append(
                        {
                            "file": f.file.relpath,
                            "line": f.lineno,
                            "function": f.qualname or f.name,
                            "domain_score": round(fm, 2),
                            "worst_type": ast.unparse(worst_ann) if worst_ann is not None else None,
                        }
                    )

        for source, cls in iter_classes(codebase):
            if source.is_test or is_private(cls.name):
                continue
            for stmt in cls.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                    target = stmt.target.id
                    if is_private(target) or is_dunder(target):
                        continue
                    annotated += 1
                    total_surface += 1
                    slot_scores.append(classify_annotation(stmt.annotation))

        if not slot_scores:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        dsr = mean(slot_scores)
        score = clamp(100.0 * dsr / TARGET_RATIO)
        coverage = annotated / total_surface if total_surface else 0.0
        violations.sort(key=lambda v: v["domain_score"])

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(dsr, 3),
            score_contribution=score,
            status="measured",
            detail={
                "domain_surface_ratio": round(dsr, 3),
                "slot_count": len(slot_scores),
                "annotation_coverage": round(coverage, 3),
                "domain_vocab_density": _domain_vocab_density(codebase),
                "target_ratio": TARGET_RATIO,
            },
            violations=violations[:50],
        )
