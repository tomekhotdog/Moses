"""Rule Params: explicit, typed knobs threaded into evaluate (behaviour-preserving)."""

from __future__ import annotations

from moses.commandments.c06_define_errors_out import (
    DefineErrorsOut,
    Params as ErrorsParams,
)
from moses.commandments.c02_loose_coupling import (
    LooseCoupling,
    Params as LooseCouplingParams,
)
from moses.commandments.c13_few_parameters import FewParameters, Params
from moses.commandments.c21_cohesive_classes import (
    CohesiveClasses,
    Params as CohesionParams,
)
from moses.commandments.c27_data_over_primitives import (
    DataOverPrimitives,
    Params as DataParams,
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


def test_c02_tighter_ramp_does_not_raise_score(bad_codebase):
    default = LooseCoupling().evaluate(bad_codebase)
    tight = LooseCoupling().evaluate(bad_codebase, LooseCouplingParams(floor=0.0, ceil=1.0))
    assert tight.score_contribution <= default.score_contribution


def test_c27_lower_target_ratio_is_more_lenient():
    from pathlib import Path

    from moses.models import Codebase, SourceFile

    text = (
        "class Repo:\n"
        "    cache: dict[str, int]\n"
        "    def find(self, uid: str) -> dict[str, int]: ...\n"
    )
    sf = SourceFile(path=Path("m.py"), relpath="m.py", text=text)
    codebase = Codebase(root=Path("."), files=[sf])
    lenient = DataOverPrimitives().evaluate(codebase, DataParams(target_ratio=0.3))
    strict = DataOverPrimitives().evaluate(codebase, DataParams(target_ratio=0.9))
    assert lenient.score_contribution >= strict.score_contribution


def test_default_rule_params_covers_all_implemented():
    from moses.commandments import ALL_COMMANDMENTS, default_rule_params

    params = default_rule_params()
    for cmd in ALL_COMMANDMENTS:
        assert cmd.number in params  # every implemented rule has default Params


def test_engine_threads_overridden_params(fixtures_dir):
    from moses.commandments.c13_few_parameters import Params
    from moses.config import Config
    from moses.engine import run

    base = run(fixtures_dir / "bad_example", Config(enabled={13}))
    strict = Config(enabled={13})
    strict.rule_params[13] = Params(param_budget=0, slope=99.0)
    tuned = run(fixtures_dir / "bad_example", strict)

    c13_base = next(c for c in base.commandments if c.number == 13)
    c13_tuned = next(c for c in tuned.commandments if c.number == 13)
    assert c13_tuned.score_contribution <= c13_base.score_contribution
