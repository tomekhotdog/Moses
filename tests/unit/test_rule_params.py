"""Rule Params: explicit, typed knobs threaded into evaluate (behaviour-preserving)."""

from __future__ import annotations

from moses.commandments.c13_few_parameters import FewParameters, Params


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
