"""CommandmentsConfig: the master scoring config (rule configs + weights)."""

from __future__ import annotations

from moses.commandments import ALL_COMMANDMENTS
from moses.commandments.c13_few_parameters import RuleConfig as C13
from moses.config import WEIGHTS, CommandmentsConfig


def test_default_covers_all_rules_and_weights():
    cc = CommandmentsConfig.default()
    for cmd in ALL_COMMANDMENTS:
        assert cmd.number in cc.configs
    assert cc.weights == WEIGHTS


def test_config_for_and_weight_for():
    cc = CommandmentsConfig.default()
    assert isinstance(cc.config_for(13), C13)
    assert cc.weight_for(13) == WEIGHTS[13]


def test_with_config_is_immutable_update():
    cc = CommandmentsConfig.default()
    cc2 = cc.with_config(13, C13(param_budget=0, slope=99.0))
    assert cc.config_for(13).param_budget == 2
    assert cc2.config_for(13).param_budget == 0
    assert cc2.weight_for(13) == cc.weight_for(13)


def test_with_weight_is_immutable_update():
    cc = CommandmentsConfig.default()
    cc2 = cc.with_weight(13, 99)
    assert cc.weight_for(13) == WEIGHTS[13]
    assert cc2.weight_for(13) == 99


def test_to_from_dict_roundtrip():
    import json
    cc = CommandmentsConfig.default().with_config(13, C13(slope=42.0)).with_weight(13, 7)
    back = CommandmentsConfig.from_dict(json.loads(json.dumps(cc.to_dict())))
    assert back.config_for(13).slope == 42.0
    assert back.weight_for(13) == 7
    assert back.configs == cc.configs   # incl. c25's frozenset field surviving JSON
    assert back.weights == cc.weights


def test_from_dict_skips_unknown_rule_numbers():
    cc = CommandmentsConfig.default()
    data = cc.to_dict()
    data["configs"]["999"] = {"bogus": 1}
    back = CommandmentsConfig.from_dict(data)
    assert 999 not in back.configs


def test_from_dict_empty_weights_falls_back():
    from moses.config import WEIGHTS
    data = CommandmentsConfig.default().to_dict()
    data["weights"] = {}
    back = CommandmentsConfig.from_dict(data)
    assert back.weights == WEIGHTS


def test_engine_threads_master_overrides(fixtures_dir):
    from moses.commandments.c13_few_parameters import RuleConfig
    from moses.config import Config
    from moses.engine import run

    base = run(fixtures_dir / "bad_example", Config(enabled={13}))
    cfg = Config(enabled={13})
    cfg.commandments = cfg.commandments.with_config(13, RuleConfig(param_budget=0, slope=99.0))
    tuned = run(fixtures_dir / "bad_example", cfg)
    b = next(c for c in base.commandments if c.number == 13)
    t = next(c for c in tuned.commandments if c.number == 13)
    assert t.score_contribution <= b.score_contribution
