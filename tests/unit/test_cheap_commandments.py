"""Each cheap rule should score the bad fixture worse than the good fixture."""

from __future__ import annotations

import pytest

from moses.commandments.c11_small_functions import SmallFunctions
from moses.commandments.c13_few_parameters import FewParameters
from moses.commandments.c14_shallow_nesting import ShallowNesting
from moses.commandments.c18_empty_catch import NoEmptyCatch
from moses.commandments.c25_magic_numbers import NoMagicNumbers

CHEAP_RULES = [SmallFunctions, ShallowNesting, NoEmptyCatch, NoMagicNumbers]


@pytest.mark.parametrize("rule_cls", CHEAP_RULES)
def test_bad_scores_worse_than_good(rule_cls, bad_codebase, good_codebase):
    bad = rule_cls().evaluate(bad_codebase, rule_cls.Params())
    good = rule_cls().evaluate(good_codebase, rule_cls.Params())
    assert bad.score_contribution <= good.score_contribution


def test_empty_catch_fires_on_bad(bad_codebase):
    result = NoEmptyCatch().evaluate(bad_codebase, NoEmptyCatch.Params())
    assert result.status == "measured"
    assert len(result.violations) >= 2
    assert result.score_contribution < 100


def test_empty_catch_clean_on_good(good_codebase):
    result = NoEmptyCatch().evaluate(good_codebase, NoEmptyCatch.Params())
    assert result.violations == []
    assert result.score_contribution == 100.0


def test_magic_numbers_fire_on_bad(bad_codebase):
    result = NoMagicNumbers().evaluate(bad_codebase, NoMagicNumbers.Params())
    assert result.metric > 0
    assert len(result.violations) > 0


def test_magic_numbers_excludes_allowed(good_codebase, bad_codebase):
    good = NoMagicNumbers().evaluate(good_codebase, NoMagicNumbers.Params())
    bad = NoMagicNumbers().evaluate(bad_codebase, NoMagicNumbers.Params())
    # 0 and 1 are never magic; good.py has far fewer magic literals per kLOC.
    assert good.metric < bad.metric


def test_small_functions_flags_long(bad_codebase):
    result = SmallFunctions().evaluate(bad_codebase, SmallFunctions.Params())
    assert any(v["loc"] > 50 for v in result.violations)


def test_few_parameters_flags_wide(bad_codebase):
    result = FewParameters().evaluate(bad_codebase, FewParameters.Params())
    assert any(v["params"] >= 4 for v in result.violations)


def test_shallow_nesting_flags_deep(bad_codebase):
    result = ShallowNesting().evaluate(bad_codebase, ShallowNesting.Params())
    assert any(v["depth"] >= 3 for v in result.violations)
