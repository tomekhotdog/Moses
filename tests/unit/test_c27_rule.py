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


def test_property_and_setter_excluded():
    text = (
        "class C:\n"
        "    @property\n"
        "    def name(self) -> str: ...\n"
        "    @name.setter\n"
        "    def name(self, v: str) -> None: ...\n"
        "    def total(self, x: int) -> str: ...\n"
    )
    result = DataOverPrimitives().evaluate(_codebase(text))
    # The property getter and its setter must not be scored; only `total` contributes.
    # `total` has param x:int (0) and return str (0) -> 2 primitive slots.
    assert result.detail["slot_count"] == 2


def test_predicate_bool_and_count_int_returns_exempt():
    text = (
        "def is_ready(self, order: 'Order') -> bool: ...\n"
        "def count(self, rows: 'Order') -> int: ...\n"
    )
    result = DataOverPrimitives().evaluate(_codebase(text))
    # Both functions take one concept param (Order -> 1.0); their bool/int returns
    # are exempt, so they are NOT counted as primitive return slots.
    assert result.detail["slot_count"] == 2
    assert result.metric == 1.0


def test_domain_vocab_density_reported():
    text = (
        "from typing import NewType\n"
        "from dataclasses import dataclass\n"
        "UserId = NewType('UserId', int)\n"
        "@dataclass\n"
        "class Order:\n"
        "    id: UserId\n"
        "    def lookup(self, uid: UserId) -> 'Order': ...\n"
    )
    result = DataOverPrimitives().evaluate(_codebase(text))
    # One class (Order) + one NewType (UserId) = 2 domain-type definitions.
    assert result.detail["domain_vocab_density"] > 0
    assert "domain_vocab_density" in result.detail


def test_none_return_is_exempt_and_not_worst_type():
    # `-> None` is the correct type for a command/procedure, not primitive obsession.
    text = "def create(self, name: str) -> None: ...\n"
    result = DataOverPrimitives().evaluate(_codebase(text))
    # Only the `name: str` param is scored; the `-> None` return is exempt.
    assert result.detail["slot_count"] == 1
    assert result.metric == 0.0
    # The violation must blame the str param, never `None`.
    assert result.violations
    assert "None" not in (result.violations[0]["worst_type"] or "")
    assert result.violations[0]["worst_type"] == "str"


def test_varargs_and_kwargs_annotations_are_scored():
    text = "def handle(self, *items: 'Order', **opts: str) -> None: ...\n"
    result = DataOverPrimitives().evaluate(_codebase(text))
    # *items: Order -> 1.0 (concept), **opts: str -> 0.0 (primitive). Both counted.
    assert result.detail["slot_count"] == 2
    assert result.metric == 0.5


def test_vocab_density_denominator_excludes_test_files():
    from pathlib import Path
    from moses.models import Codebase, SourceFile

    src = SourceFile(path=Path("m.py"), relpath="m.py", text="class Order:\n    x: int\n")
    test = SourceFile(
        path=Path("tests/test_m.py"),
        relpath="tests/test_m.py",
        text="def test_a():\n    assert True\n" * 50,
    )
    cb = Codebase(root=Path("."), files=[src, test])
    result = DataOverPrimitives().evaluate(cb)
    # Density must be computed over source-only LOC; the big test file must not dilute it.
    # Order class over ~2 non-blank source LOC -> density ~ 500 (defs per kLOC), well above 1.
    assert result.detail["domain_vocab_density"] > 100
