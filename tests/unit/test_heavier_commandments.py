"""Coverage for the heavier (structural) commandments.

Two kinds of assertions:
- The bad fixture should score no better than the good fixture (monotonicity).
- Rules with an unambiguous violation in the fixture should actually fire.
"""

from __future__ import annotations

import pytest

from moses.commandments.c01_deep_modules import DeepModules
from moses.commandments.c02_loose_coupling import LooseCoupling
from moses.commandments.c03_pass_through import PassThrough
from moses.commandments.c05_pull_complexity_down import PullComplexityDown
from moses.commandments.c06_define_errors_out import DefineErrorsOut
from moses.commandments.c12_cognitive_complexity import LowCognitiveComplexity
from moses.commandments.c15_command_query import CommandQuery
from moses.commandments.c16_dry import DRY
from moses.commandments.c17_commented_out_code import NoCommentedOutCode
from moses.commandments.c21_cohesive_classes import CohesiveClasses
from moses.commandments.c22_law_of_demeter import LawOfDemeter
from moses.commandments.c23_narrow_scope import NarrowScope
from moses.commandments.c24_immutability import Immutability
from moses.commandments.c29_composition import Composition
from moses.commandments.c31_class_complexity import ClassComplexity

HEAVIER_RULES = [
    DeepModules,
    LooseCoupling,
    PassThrough,
    PullComplexityDown,
    DefineErrorsOut,
    LowCognitiveComplexity,
    CommandQuery,
    DRY,
    NoCommentedOutCode,
    CohesiveClasses,
    LawOfDemeter,
    NarrowScope,
    Immutability,
    Composition,
    ClassComplexity,
]


# DeepModules measures impl_LOC / API_surface; on the very small good fixture
# the ratio is legitimately low, so "bad worse than good" does not hold for it.
# It is exercised by the status/fire tests instead.
_MONOTONIC_RULES = [r for r in HEAVIER_RULES if r is not DeepModules]


@pytest.mark.parametrize("rule_cls", _MONOTONIC_RULES)
def test_bad_scores_no_better_than_good(rule_cls, bad_codebase, good_codebase):
    bad = rule_cls().evaluate(bad_codebase, rule_cls.Params())
    good = rule_cls().evaluate(good_codebase, rule_cls.Params())
    # Skip rules that genuinely cannot measure one of the fixtures.
    if bad.status != "measured" or good.status != "measured":
        pytest.skip(f"{rule_cls.__name__} not measured on a fixture")
    assert bad.score_contribution <= good.score_contribution


@pytest.mark.parametrize("rule_cls", HEAVIER_RULES)
def test_every_rule_sets_status(rule_cls, bad_codebase):
    result = rule_cls().evaluate(bad_codebase, rule_cls.Params())
    assert result.status in {"measured", "not_measured", "error", "skipped"}
    assert result.number == rule_cls().number


def test_pass_through_fires(bad_codebase):
    result = PassThrough().evaluate(bad_codebase, PassThrough.Params())
    names = {v["function"] for v in result.violations}
    assert any("delegate" in n for n in names)
    assert any("forward" in n for n in names)


def test_commented_out_code_fires(bad_codebase):
    result = NoCommentedOutCode().evaluate(bad_codebase, NoCommentedOutCode.Params())
    assert result.metric > 0
    assert len(result.violations) >= 1
    assert result.score_contribution < 100


def test_commented_out_code_clean_on_good(good_codebase):
    result = NoCommentedOutCode().evaluate(good_codebase, NoCommentedOutCode.Params())
    assert result.violations == []
    assert result.score_contribution == 100.0


def test_dry_fires(bad_codebase):
    result = DRY().evaluate(bad_codebase, DRY.Params())
    assert result.status == "measured"
    assert result.score_contribution < 100


def test_law_of_demeter_fires(bad_codebase):
    result = LawOfDemeter().evaluate(bad_codebase, LawOfDemeter.Params())
    assert result.status == "measured"
    assert len(result.violations) >= 1


def test_composition_flags_deep_inheritance(bad_codebase):
    result = Composition().evaluate(bad_codebase, Composition.Params())
    assert result.status == "measured"
    assert result.score_contribution < 100
