# Master CommandmentsConfig + Calibration Scaffolding Plan

> **For Claude:** REQUIRED SUB-SKILL: Use tomek-superpowers:build to implement this plan task-by-task.

**Goal:** Rename per-rule `Params`→`RuleConfig`, introduce a master `CommandmentsConfig` (rule configs + weights) on `Config.commandments`, thread it through the engine, and scaffold `evals/calibrate.py`.
**Architecture:** Each rule keeps a frozen dataclass (renamed `RuleConfig`). `CommandmentsConfig` (config.py) owns `{number: RuleConfig}` + `weights` with `config_for`/`weight_for`/`with_*`/`default`/`to_dict`/`from_dict`. `Config.commandments` replaces `rule_params`; engine reads `config.commandments.config_for(n)` and `_weighted_score` reads `config.commandments.weight_for(n)`.
**Tech Stack:** Python stdlib dataclasses; pytest.
**Design:** `docs/plans/2026-06-25-commandments-config-design.md`

Work on `main`. Tests: `uv run pytest`. **Behaviour-preservation gate after every task:** `uv run pytest -q` green AND `uv run python evals/corpus_score.py --corpus evals/corpus --year 2024` then `git diff --stat evals/corpus/moses_scores.json` EMPTY. Do not commit `moses_scores.json`.

---

### Task 1: Rename `Params` → `RuleConfig` everywhere (mechanical) — ✅ COMPLETE (446946f)
**Depends on:** none

Pure rename, no behaviour change. Across all 21 implemented rule modules `src/moses/commandments/cNN_*.py`:
- Rename the `class Params` → `class RuleConfig` (keep all fields/defaults).
- Rename the class attribute `Params = Params` → `RuleConfig = RuleConfig`.
- Rename the `evaluate` parameter: `def evaluate(self, codebase, params: Params)` → `def evaluate(self, codebase, config: RuleConfig)`, and update body references `params.X` → `config.X`. (For c20's empty one: `config: RuleConfig`.)

In `src/moses/commandments/__init__.py`:
- Rename `default_rule_params()` → `default_rule_configs()`, building `{cmd.number: cmd.RuleConfig()}`.

In `src/moses/config.py`:
- The `_default_rule_params` helper → `_default_rule_configs` (calls `default_rule_configs`). Keep `Config.rule_params` field name FOR NOW but its default_factory uses `_default_rule_configs` (it still holds RuleConfig instances). (Task 2 renames the field.)

In `src/moses/engine.py`:
- The fallback `cmd.Params()` → `cmd.RuleConfig()`.

In tests: update every `import ... Params`, `Cls.Params()`, and `from cNN import Params` to `RuleConfig`. Find them: `grep -rn "Params" tests/ src/moses`. After rename, `grep -rn "\bParams\b" src/ tests/` should return NOTHING.

**Verification:** behaviour gate (suite green + corpus byte-identical). `grep -rn "\bParams\b" src/ tests/` empty.

**Commit:**
```bash
git add src/moses tests/
git commit -m "refactor(rules): rename per-rule Params -> RuleConfig"
```

---

### Task 2: Introduce `CommandmentsConfig` and thread it — ✅ COMPLETE (272aef5, fixes c13443d)
**Depends on:** Task 1

**Files:**
- Modify: `src/moses/config.py` (add `CommandmentsConfig`, replace `Config.rule_params` → `Config.commandments`)
- Modify: `src/moses/engine.py` (read the master)
- Test: `tests/unit/test_commandments_config.py`

**Step 1: Write the failing test**
```python
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
    assert cc.config_for(13).param_budget == 2     # original unchanged
    assert cc2.config_for(13).param_budget == 0
    assert cc2.weight_for(13) == cc.weight_for(13)  # weights carried over


def test_with_weight_is_immutable_update():
    cc = CommandmentsConfig.default()
    cc2 = cc.with_weight(13, 99)
    assert cc.weight_for(13) == WEIGHTS[13]
    assert cc2.weight_for(13) == 99


def test_to_from_dict_roundtrip():
    cc = CommandmentsConfig.default().with_config(13, C13(slope=42.0)).with_weight(13, 7)
    back = CommandmentsConfig.from_dict(cc.to_dict())
    assert back.config_for(13).slope == 42.0
    assert back.weight_for(13) == 7
    assert back.configs == cc.configs
    assert back.weights == cc.weights


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
```

**Step 2: Run to verify it fails**
`uv run pytest tests/unit/test_commandments_config.py -q` → FAIL (no `CommandmentsConfig`).

**Step 3: Implement** — in `src/moses/config.py` add (after `WEIGHTS`/`MVP_COMMANDMENTS`, before `Config`):
```python
from dataclasses import asdict


def _default_rule_configs() -> dict:
    from .commandments import default_rule_configs

    return default_rule_configs()


@dataclass(frozen=True)
class CommandmentsConfig:
    """Master scoring config: every rule's RuleConfig plus the Weights."""

    configs: dict  # number -> that rule's RuleConfig
    weights: dict  # number -> relative importance (int)

    @classmethod
    def default(cls) -> "CommandmentsConfig":
        return cls(configs=_default_rule_configs(), weights=dict(WEIGHTS))

    def config_for(self, number: int):
        return self.configs.get(number)

    def weight_for(self, number: int) -> int:
        return self.weights.get(number, 0)

    def with_config(self, number: int, rule_config) -> "CommandmentsConfig":
        configs = dict(self.configs)
        configs[number] = rule_config
        return CommandmentsConfig(configs=configs, weights=dict(self.weights))

    def with_weight(self, number: int, weight: int) -> "CommandmentsConfig":
        weights = dict(self.weights)
        weights[number] = weight
        return CommandmentsConfig(configs=dict(self.configs), weights=weights)

    def to_dict(self) -> dict:
        return {
            "weights": dict(self.weights),
            "configs": {n: asdict(rc) for n, rc in self.configs.items()},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CommandmentsConfig":
        defaults = _default_rule_configs()
        configs = {}
        for n, fields in data.get("configs", {}).items():
            n = int(n)
            rc_type = type(defaults[n])
            configs[n] = rc_type(**fields)
        # fill any rule absent from the dict with its default
        for n, rc in defaults.items():
            configs.setdefault(n, rc)
        weights = {int(k): int(v) for k, v in data.get("weights", WEIGHTS).items()}
        return cls(configs=configs, weights=weights)
```
Replace the `Config.rule_params` field with:
```python
    commandments: CommandmentsConfig = field(default_factory=CommandmentsConfig.default)
```
(remove the old `rule_params` field and the `_default_rule_params` helper if now unused). In `with_overrides`, carry `commandments=self.commandments` through. `from_file` constructs `Config()` (default_factory builds `commandments`) then mutates other fields — leave `commandments` intact.

In `src/moses/engine.py`:
- Call site: `params = config.rule_params.get(number) ...` → 
```python
        rule_config = config.commandments.config_for(number)
        if rule_config is None:
            rule_config = cmd.RuleConfig()
        try:
            result = cmd.evaluate(codebase, rule_config)
```
- `_weighted_score(results, config)` — replace `num += r.weight * r.score_contribution` with `num += config.commandments.weight_for(r.number) * r.score_contribution` and `den += config.commandments.weight_for(r.number)`. (Default weights == WEIGHTS, so identical.) Ensure `_weighted_score` still receives `config` (it does).

**Step 4: Run tests + gate**
`uv run pytest tests/unit/test_commandments_config.py -q` → PASS. Then full suite green + corpus byte-identical. Update any test still referencing `Config(...).rule_params` → `.commandments` (grep `rule_params` in tests/ and fix; e.g. the Task-4-era `test_rule_params.py` engine test and `test_engine.py` fallback test, and `test_loader_config_models.py`'s `len(cfg.rule_params)` → `len(cfg.commandments.configs)`).

**Step 5: Commit**
```bash
git add src/moses/config.py src/moses/engine.py tests/
git commit -m "feat(config): master CommandmentsConfig (rule configs + weights) threaded through engine"
```

---

### Task 3: Calibration scaffolding (`evals/calibrate.py`, skeleton only) — ✅ COMPLETE (66feaa1, usage fix)
**Depends on:** Task 2

**Files:**
- Create: `evals/calibrate.py`
- Test: `tests/unit/test_calibrate.py`

**Step 1: Write the failing test**
```python
"""calibrate scaffolding: agreement metric + baseline report."""

from __future__ import annotations

import json
from pathlib import Path

from evals.calibrate import agreement, report_baseline


def test_agreement_perfect():
    a = agreement([(85.0, 88.0), (40.0, 30.0), (60.0, 70.0)])
    assert a["spearman"] == 1.0
    assert a["mean_abs_gap"] == round((3 + 10 + 10) / 3, 2)


def test_report_baseline_over_corpus(tmp_path):
    root = tmp_path / "corpus"
    (root / "2024" / "q1").mkdir(parents=True)
    merged = {
        "year": "2024",
        "questions": {
            "q1": {
                "good.py": {"moses_score": 85.0, "judge_pct": 88},
                "bad.py": {"moses_score": 40.0, "judge_pct": 30},
            }
        },
    }
    (root / "comparison.json").write_text(json.dumps(merged), encoding="utf-8")
    out = report_baseline(root)
    assert "q1" in out
    assert "spearman" in out.lower()
```

**Step 2: Run to verify it fails** → `uv run pytest tests/unit/test_calibrate.py -q` → FAIL.

**Step 3: Implement** `evals/calibrate.py`:
```python
"""Calibration harness (SCAFFOLDING). Reports current Moses-vs-Judge agreement.

The optimiser is intentionally a stub for now: it returns the default
CommandmentsConfig unchanged. The real search over CommandmentsConfig (rule
configs + weights) lands once the corpus is scaled beyond the 3-question pilot.

Usage: uv run python evals/calibrate.py --corpus evals/corpus --year 2024
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from evals.corpus_report import rank_agreement


def agreement(pairs: list[tuple[float, float]]) -> dict:
    """Spearman rho + mean absolute (Moses - Judge) gap over (moses, judge) pairs."""
    rho = rank_agreement(pairs)["spearman"]
    gap = (
        round(sum(abs(m - j) for m, j in pairs) / len(pairs), 2) if pairs else None
    )
    return {"spearman": rho, "mean_abs_gap": gap, "n": len(pairs)}


def report_baseline(corpus_root: Path, year: str = "2024") -> str:
    """Human-readable report of current agreement per question + overall."""
    corpus_root = Path(corpus_root)
    data = json.loads((corpus_root / "comparison.json").read_text(encoding="utf-8"))
    lines = ["# Calibration baseline (Moses vs Judge)", ""]
    all_pairs: list[tuple[float, float]] = []
    for qname, rows in data["questions"].items():
        pairs = [
            (r["moses_score"], float(r["judge_pct"]))
            for r in rows.values()
            if r.get("judge_pct") is not None
        ]
        all_pairs.extend(pairs)
        a = agreement(pairs)
        lines.append(f"- {qname}: spearman={a['spearman']} mean_abs_gap={a['mean_abs_gap']} (n={a['n']})")
    overall = agreement(all_pairs)
    lines.append("")
    lines.append(f"Overall: spearman={overall['spearman']} mean_abs_gap={overall['mean_abs_gap']} (n={overall['n']})")
    return "\n".join(lines)


def optimize(corpus_root: Path, year: str = "2024"):
    """STUB. Returns the default CommandmentsConfig unchanged.

    TODO(phase-2b): search CommandmentsConfig (rule configs + weights) to minimise
    mean_abs_gap / maximise spearman across the corpus, re-scoring via
    moses.engine.run with the candidate config. Requires the larger corpus.
    """
    from moses.config import CommandmentsConfig

    return CommandmentsConfig.default()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="evals/corpus")
    parser.add_argument("--year", default="2024")
    args = parser.parse_args(argv)
    print(report_baseline(Path(args.corpus), args.year))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 4: Run tests + smoke** → `uv run pytest tests/unit/test_calibrate.py -q` PASS; full suite green; `uv run python evals/calibrate.py --corpus evals/corpus --year 2024` prints the baseline (q4/q9/q16 + overall). Corpus byte-identical (calibrate doesn't re-score).

**Step 5: Commit**
```bash
git add evals/calibrate.py tests/unit/test_calibrate.py
git commit -m "feat(calibrate): scaffolding — agreement metric + baseline report (optimiser stub)"
```

---

## Review
- [x] Code review requested — focused review of CommandmentsConfig + engine threading + rename
- [x] All feedback addressed (JSON-safe to_dict/from_dict for c25 frozenset; from_dict skips unknown rules + empty-weights fallback; hotspots + error path use master weights)
- [x] Final verification (`uv run pytest` → 155 passed/1 skipped; corpus `moses_scores.json` byte-identical; `calibrate.py` baseline overall ρ=0.365, gap 23.1)
