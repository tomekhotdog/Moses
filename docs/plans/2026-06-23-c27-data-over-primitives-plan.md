# C27 — Data over primitives Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use tomek-superpowers:build to implement this plan task-by-task.

**Goal:** Fill the `not_measured` C27 slot with a deterministic Domain Surface Ratio that rewards expressing a codebase's public type surface in domain concepts rather than raw primitives.
**Architecture:** A pure annotation classifier (`classify_annotation`) scores each AST annotation in [0,1] with container recursion; the `DataOverPrimitives` rule extracts public/annotated parameter, return, and attribute slots, averages their scores into the DSR, and curves it against `TARGET_RATIO`. No `Config` is threaded (rules can't read it — see lessons); the target is a module constant.
**Tech Stack:** Python stdlib `ast`, existing `_ast_helpers`, pytest.
**Design:** `docs/plans/2026-06-23-c27-data-over-primitives-design.md`

Run tests with `python -m pytest` (pythonpath is set to `src` via `pyproject.toml`). If imports misbehave under a sandbox, use `uv run pytest` with the sandbox disabled (see `lessons.md`).

---

### Task 1: Annotation classifier (the pure core)
**Depends on:** none

**Files:**
- Create: `src/moses/commandments/c27_data_over_primitives.py` (classifier portion only this task)
- Test: `tests/unit/test_c27_classifier.py`

**Step 1: Write the failing test**
```python
"""C27 annotation classifier: domain-richness of a single annotation in [0,1]."""

from __future__ import annotations

import ast

import pytest

from moses.commandments.c27_data_over_primitives import classify_annotation


def _ann(src: str) -> ast.expr:
    """Parse `x: <src>` and return the annotation node."""
    mod = ast.parse(f"x: {src}")
    return mod.body[0].annotation  # type: ignore[attr-defined]


@pytest.mark.parametrize(
    "src, expected",
    [
        # primitives / erased -> 0
        ("int", 0.0),
        ("str", 0.0),
        ("bool", 0.0),
        ("None", 0.0),
        ("Any", 0.0),
        ("dict", 0.0),
        ("list", 0.0),
        # concepts -> 1
        ("UserId", 1.0),
        ("Order", 1.0),
        ("datetime", 1.0),
        ("Decimal", 1.0),
        # weak -> 0.5
        ("Literal['a', 'b']", 0.5),
        # containers score by element / args
        ("list[Order]", 1.0),
        ("list[int]", 0.0),
        ("set[Customer]", 1.0),
        ("dict[UserId, Money]", 1.0),
        ("dict[str, int]", 0.0),
        ("dict[str, Order]", 0.0),          # min: key is primitive
        ("tuple[Order, Customer]", 1.0),
        ("tuple[int, int]", 0.0),
        ("tuple[Order, ...]", 1.0),
        # Optional / unions: None is stripped, nullability is not obsession
        ("Optional[Order]", 1.0),
        ("Order | None", 1.0),
        ("int | None", 0.0),
        ("Order | Customer", 1.0),
        ("int | str", 0.0),
        # typing-cased aliases
        ("List[Order]", 1.0),
        ("Dict[str, int]", 0.0),
    ],
)
def test_classify_annotation(src, expected):
    assert classify_annotation(_ann(src)) == expected


def test_none_node_is_zero():
    assert classify_annotation(None) == 0.0


def test_container_ordering():
    # The load-bearing nuance: collection-of-concept beats primitive-valued map.
    assert classify_annotation(_ann("list[Order]")) > classify_annotation(_ann("dict[str, int]"))
    assert classify_annotation(_ann("dict[str, int]")) == classify_annotation(_ann("int"))
```

**Step 2: Run test to verify it fails**
Run: `python -m pytest tests/unit/test_c27_classifier.py -q`
Expected: FAIL (ModuleNotFoundError / ImportError: cannot import `classify_annotation`)

**Step 3: Write minimal implementation**
Create `src/moses/commandments/c27_data_over_primitives.py`:
```python
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
```

**Step 4: Run test to verify it passes**
Run: `python -m pytest tests/unit/test_c27_classifier.py -q`
Expected: PASS (all parametrized cases green)

**Step 5: Commit**
```bash
git add src/moses/commandments/c27_data_over_primitives.py tests/unit/test_c27_classifier.py
git commit -m "feat(c27): annotation classifier with container recursion"
```

---

### Task 2: The DataOverPrimitives rule + registration
**Depends on:** Task 1

**Files:**
- Modify: `src/moses/commandments/c27_data_over_primitives.py`
- Modify: `src/moses/commandments/__init__.py`
- Test: `tests/unit/test_c27_rule.py`

**Step 1: Write the failing test**
```python
"""C27 rule: DSR over public annotated slots, curve, violations, details."""

from __future__ import annotations

from pathlib import Path

from moses.commandments.c27_data_over_primitives import DataOverPrimitives
from moses.models import Codebase, SourceFile


def _codebase(text: str) -> Codebase:
    sf = SourceFile(path=Path("m.py"), relpath="m.py", text=text)
    return Codebase(root=Path("."), files=[sf])


WELL_MODELLED = '''
from dataclasses import dataclass

@dataclass
class Order:
    id: int

class Repo:
    cache: dict["UserId", Order]
    def find(self, uid: "UserId") -> Order: ...
    def all_orders(self) -> list[Order]: ...
'''

PRIMITIVE_HEAVY = '''
class Repo:
    cache: dict[str, int]
    def find(self, uid: str) -> dict[str, int]: ...
    def totals(self, rows: list[str]) -> dict[str, int]: ...
'''


def test_well_modelled_scores_high():
    result = DataOverPrimitives().evaluate(_codebase(WELL_MODELLED))
    assert result.status == "measured"
    assert result.metric > 0.7
    assert result.score_contribution > 90


def test_primitive_heavy_scores_low():
    result = DataOverPrimitives().evaluate(_codebase(PRIMITIVE_HEAVY))
    assert result.status == "measured"
    assert result.metric < 0.2
    assert result.score_contribution < 35
    assert any("dict[str, int]" in (v.get("worst_type") or "") for v in result.violations)


def test_well_beats_primitive():
    well = DataOverPrimitives().evaluate(_codebase(WELL_MODELLED))
    prim = DataOverPrimitives().evaluate(_codebase(PRIMITIVE_HEAVY))
    assert well.score_contribution > prim.score_contribution


def test_no_annotations_is_not_measured():
    result = DataOverPrimitives().evaluate(_codebase("def f(a, b):\n    return a + b\n"))
    assert result.status == "not_measured"


def test_private_and_dunder_excluded():
    text = "class C:\n    def _hidden(self, x: str) -> str: ...\n    def __eq__(self, o: object) -> bool: ...\n"
    result = DataOverPrimitives().evaluate(_codebase(text))
    # Only excluded members exist -> nothing to measure.
    assert result.status == "not_measured"


def test_coverage_reported():
    text = 'def f(a: "Order", b) -> "Order": ...\n'  # b is unannotated
    result = DataOverPrimitives().evaluate(_codebase(text))
    assert result.detail["annotation_coverage"] < 1.0
    assert result.detail["target_ratio"] == 0.6
```

**Step 2: Run test to verify it fails**
Run: `python -m pytest tests/unit/test_c27_rule.py -q`
Expected: FAIL (ImportError: cannot import `DataOverPrimitives`)

**Step 3: Write minimal implementation**
Append to `src/moses/commandments/c27_data_over_primitives.py`:
```python
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
            if not _exempt_return(f.name, ret):
                total_surface += 1
                if ret is not None:
                    annotated += 1
                    s = classify_annotation(ret)
                    slot_scores.append(s)
                    fn_scores.append(s)
                    if s < worst_score:
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
```

Then register it in `src/moses/commandments/__init__.py` — add the import beside the others and the instance in `ALL_COMMANDMENTS` (place after `NoMagicNumbers()` / before `Composition()` to keep rough numeric order):
```python
from .c27_data_over_primitives import DataOverPrimitives
```
```python
    NoMagicNumbers(),
    DataOverPrimitives(),
    Composition(),
```

**Step 4: Run test to verify it passes**
Run: `python -m pytest tests/unit/test_c27_rule.py -q`
Expected: PASS

**Step 5: Commit**
```bash
git add src/moses/commandments/c27_data_over_primitives.py src/moses/commandments/__init__.py tests/unit/test_c27_rule.py
git commit -m "feat(c27): DataOverPrimitives rule + registration"
```

---

### Task 3: Fixtures + end-to-end engine integration
**Depends on:** Task 2

**Files:**
- Create: `tests/fixtures/well_modelled/well.py`
- Create: `tests/fixtures/primitive_heavy/prim.py`
- Test: `tests/unit/test_c27_e2e.py`

**Step 1: Write the failing test**
```python
"""C27 over real fixture trees, and through the full engine run."""

from __future__ import annotations

from pathlib import Path

from moses.commandments.c27_data_over_primitives import DataOverPrimitives
from moses.config import Config
from moses.engine import run
from moses.loader import load_codebase

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_fixture_ranking():
    well = DataOverPrimitives().evaluate(load_codebase(FIXTURES / "well_modelled"))
    prim = DataOverPrimitives().evaluate(load_codebase(FIXTURES / "primitive_heavy"))
    assert well.status == prim.status == "measured"
    assert well.score_contribution > prim.score_contribution


def test_engine_includes_c27_measured():
    cfg = Config(enabled={27})
    verdict = run(FIXTURES / "well_modelled", cfg)
    c27 = next(c for c in verdict.commandments if c.number == 27)
    assert c27.status == "measured"
    assert c27.detail["target_ratio"] == 0.6
```

**Step 2: Run test to verify it fails**
Run: `python -m pytest tests/unit/test_c27_e2e.py -q`
Expected: FAIL (fixture directories do not exist → load_codebase yields empty → not_measured / StopIteration)

**Step 3: Create the fixtures**

`tests/fixtures/well_modelled/well.py`:
```python
"""Well-modelled domain: concepts everywhere, primitives wrapped."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import NewType

UserId = NewType("UserId", int)


class Status(Enum):
    OPEN = "open"
    CLOSED = "closed"


@dataclass
class Money:
    amount: Decimal
    currency: str


@dataclass
class Order:
    id: UserId
    total: Money
    status: Status


class OrderBook:
    orders: dict[UserId, Order]

    def place(self, owner: UserId, total: Money) -> Order:
        ...

    def for_owner(self, owner: UserId) -> list[Order]:
        ...

    def balance(self, owner: UserId) -> Money:
        ...
```

`tests/fixtures/primitive_heavy/prim.py`:
```python
"""Primitive-obsessed: meaning smeared across str/int/dict."""

from __future__ import annotations


class OrderBook:
    orders: dict[str, int]

    def place(self, owner: str, total: float, currency: str) -> dict[str, int]:
        ...

    def for_owner(self, owner: str) -> list[str]:
        ...

    def summary(self, rows: list[str]) -> tuple[int, int, str]:
        ...
```

**Step 4: Run test to verify it passes**
Run: `python -m pytest tests/unit/test_c27_e2e.py -q`
Expected: PASS

**Step 5: Full-suite regression check**
Run: `python -m pytest -q`
Expected: PASS — all previously-passing tests still green (1 pre-existing skip is fine). C27 is now implemented, so the count of `not_measured` placeholders drops by one; confirm no existing test asserted C27 was `not_measured`.

**Step 6: Self-host sanity check**
Run: `python -m moses judge . --exclude 'tests/fixtures/*'`
Expected: exits 0; C27 now shows `status="measured"` in the report rather than `not_measured`. Note the new Score (C27 entering the weighted mean may move it); confirm the grade has not regressed below B, and if it did, capture the C27 violations as the explanation (do not silently mask).

**Step 7: Commit**
```bash
git add tests/fixtures/well_modelled tests/fixtures/primitive_heavy tests/unit/test_c27_e2e.py
git commit -m "test(c27): fixtures + end-to-end engine integration"
```

---

## Review
- [ ] Code review requested (five-axis)
- [ ] All feedback addressed
- [ ] Final verification passed (`python -m pytest -q` green; `moses judge .` self-host still ≥ B)
