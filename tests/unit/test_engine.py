"""Engine integration: weighted mean, enabled-only averaging, error handling."""

from __future__ import annotations

from moses.config import Config
from moses.engine import _weighted_score, run
from moses.models import CommandmentResult, grade_for


def test_run_on_good_scores_high(fixtures_dir):
    verdict = run(fixtures_dir / "good_example")
    assert verdict.score > 80
    assert verdict.grade == "A"


def test_run_on_bad_scores_lower_than_good(fixtures_dir):
    bad = run(fixtures_dir / "bad_example")
    good = run(fixtures_dir / "good_example")
    assert bad.score < good.score


def test_weighted_score_averages_enabled_measured_only():
    config = Config(enabled={11, 13})
    results = [
        CommandmentResult(11, "a", 2, 50.0, 50.0, "measured"),
        CommandmentResult(13, "b", 4, 100.0, 100.0, "measured"),
        # disabled rule must not count even though measured
        CommandmentResult(25, "c", 2, 0.0, 0.0, "measured"),
        # not_measured never counts
        CommandmentResult(14, "d", 2, None, 100.0, "not_measured"),
    ]
    # (2*50 + 4*100) / (2+4) = 500/6
    assert abs(_weighted_score(results, config) - (500 / 6)) < 1e-9


def test_disabling_does_not_pad_with_free_hundreds():
    cfg_all = Config(enabled={11, 13, 25})
    cfg_two = Config(enabled={11, 13})
    results = [
        CommandmentResult(11, "a", 2, 50.0, 50.0, "measured"),
        CommandmentResult(13, "b", 4, 50.0, 50.0, "measured"),
        CommandmentResult(25, "c", 2, 0.0, 0.0, "measured"),
    ]
    # Disabling #25 must raise (not keep flat by padding 100s).
    assert _weighted_score(results, cfg_two) > _weighted_score(results, cfg_all)


def test_error_rule_does_not_crash(monkeypatch, fixtures_dir):
    import moses.engine as engine_mod

    class Exploding:
        number = 11
        name = "boom"
        weight = 2
        RuleConfig = type("RuleConfig", (), {})

        def evaluate(self, codebase, params=None):
            raise RuntimeError("kaboom")

    monkeypatch.setattr(engine_mod, "ALL_COMMANDMENTS", [Exploding()])
    verdict = run(fixtures_dir / "good_example", Config(enabled={11}))
    err = next(c for c in verdict.commandments if c.number == 11)
    assert err.status == "error"
    assert "kaboom" in err.detail["error"]


def test_engine_fallback_when_rule_params_missing(fixtures_dir):
    from moses.config import CommandmentsConfig, WEIGHTS

    cfg = Config(enabled={13})
    # empty configs map -> engine must fall back to cmd.RuleConfig()
    cfg.commandments = CommandmentsConfig(configs={}, weights=dict(WEIGHTS))
    verdict = run(fixtures_dir / "good_example", cfg)
    c13 = next(c for c in verdict.commandments if c.number == 13)
    assert c13.status == "measured"  # fallback supplied default RuleConfig, rule ran


def test_meta_and_overview_present(fixtures_dir):
    verdict = run(fixtures_dir / "good_example")
    assert verdict.overview["file_count"] >= 1
    assert verdict.meta["tool_version"]
    assert "platform" in verdict.meta


def test_mutation_rule_is_opt_in(fixtures_dir):
    # Without --deep, #20 must be not_measured (never penalises the Score).
    shallow = run(fixtures_dir / "good_example")
    mut = next(c for c in shallow.commandments if c.number == 20)
    assert mut.status == "not_measured"


def test_config_gates_mutation_behind_deep():
    assert Config().is_enabled(20) is False
    assert Config(deep=True).is_enabled(20) is True


def test_grade_thresholds():
    assert grade_for(80) == "A"
    assert grade_for(79.9) == "B"
    assert grade_for(65) == "B"
    assert grade_for(50) == "C"
    assert grade_for(35) == "D"
    assert grade_for(20) == "E"
    assert grade_for(19.9) == "F"


def test_weight_override_affects_hotspots(fixtures_dir):
    # Rule 16 (DRY) fires heavily on bad_example; overriding its master weight
    # must change hotspot severities, proving hotspots read the master weights.
    cfg = Config()
    cfg.commandments = cfg.commandments.with_weight(16, 99)
    base = run(fixtures_dir / "bad_example")
    tuned = run(fixtures_dir / "bad_example", cfg)
    assert base.hotspots != tuned.hotspots
