"""C27 over real fixture trees, and through the full engine run."""

from __future__ import annotations

from pathlib import Path

from moses.commandments.c27_data_over_primitives import DataOverPrimitives
from moses.config import Config
from moses.engine import run
from moses.loader import load_codebase

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"


def test_fixture_ranking():
    well = DataOverPrimitives().evaluate(load_codebase(FIXTURES / "well_modelled"), DataOverPrimitives.Params())
    prim = DataOverPrimitives().evaluate(load_codebase(FIXTURES / "primitive_heavy"), DataOverPrimitives.Params())
    assert well.status == prim.status == "measured"
    assert well.score_contribution > prim.score_contribution


def test_engine_includes_c27_measured():
    cfg = Config(enabled={27})
    verdict = run(FIXTURES / "well_modelled", cfg)
    c27 = next(c for c in verdict.commandments if c.number == 27)
    assert c27.status == "measured"
    assert c27.detail["target_ratio"] == 0.6
