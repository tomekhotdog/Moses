"""Rule Params: explicit, typed knobs threaded into evaluate (behaviour-preserving)."""

from __future__ import annotations

from moses.commandments.c06_define_errors_out import (
    DefineErrorsOut,
    Params as ErrorsParams,
)
from moses.commandments.c13_few_parameters import FewParameters, Params
from moses.commandments.c21_cohesive_classes import (
    CohesiveClasses,
    Params as CohesionParams,
)


def test_c13_default_params_unchanged(bad_codebase):
    a = FewParameters().evaluate(bad_codebase)
    b = FewParameters().evaluate(bad_codebase, Params())
    assert a.score_contribution == b.score_contribution
    assert a.metric == b.metric


def test_c13_override_param_budget_changes_score(bad_codebase):
    strict = FewParameters().evaluate(bad_codebase, Params(param_budget=0))
    lenient = FewParameters().evaluate(bad_codebase, Params(param_budget=10))
    assert lenient.score_contribution >= strict.score_contribution


def test_c13_override_slope_changes_score(bad_codebase):
    gentle = FewParameters().evaluate(bad_codebase, Params(slope=1.0))
    harsh = FewParameters().evaluate(bad_codebase, Params(slope=99.0))
    assert gentle.score_contribution >= harsh.score_contribution


def test_c06_steeper_slope_does_not_raise_score(bad_codebase):
    harsh = DefineErrorsOut().evaluate(bad_codebase, ErrorsParams(slope=99.0))
    gentle = DefineErrorsOut().evaluate(bad_codebase, ErrorsParams(slope=1.0))
    assert harsh.score_contribution <= gentle.score_contribution


def test_c21_larger_budget_does_not_lower_score(bad_codebase):
    lenient = CohesiveClasses().evaluate(bad_codebase, CohesionParams(budget=10.0))
    strict = CohesiveClasses().evaluate(bad_codebase, CohesionParams(budget=0.0))
    assert lenient.score_contribution >= strict.score_contribution
