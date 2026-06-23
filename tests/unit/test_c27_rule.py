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
