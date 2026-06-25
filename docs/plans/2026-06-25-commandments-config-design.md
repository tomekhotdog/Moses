# Master CommandmentsConfig + Calibration Scaffolding Design

## Research

Builds directly on the just-completed Phase-2a refactor (this session). Current state:
- Every rule defines a frozen `Params` dataclass (class attr `Params`), required in
  `evaluate(self, codebase, params)`.
- `default_rule_params() -> dict[int, Params]` in `commandments/__init__.py`.
- `Config.rule_params: dict[int, object]` (config.py) threaded by the engine via
  `config.rule_params.get(number) or cmd.Params()` (`engine.py:117`).
- Weights live as module-level `WEIGHTS` (config.py) and reach scoring through each
  rule's `weight` property → `CommandmentResult.weight` → `_weighted_score`
  (`engine.py:42`, uses `r.weight`).

The loose `rule_params` dict and the separate module-level `WEIGHTS` are two
scattered scoring surfaces. Calibration (Phase 2b) wants ONE object to mutate and
serialize.

## Problem Statement

There is no single object representing "the full scoring configuration." Per-rule
knobs live in a bare dict on `Config`; weights live in a module constant consumed
via a different path. Calibration needs a master object it can tune (rule configs +
weights), serialize to disk (save a tuned set), and load back.

## Solution

Introduce a master **`CommandmentsConfig`** owning both scoring concerns as
separate fields, and rename the per-rule element from `Params` to `RuleConfig`.

### Vocabulary (per user)

- **RuleConfig** — a single rule's configuration: the knobs that tweak *how* that
  heuristic scores (budgets, thresholds, curve slopes). Per-rule frozen dataclass.
- **Weight** — *how important* a rule is relative to the others (unchanged meaning).
- **CommandmentsConfig** — the master object holding every rule's `RuleConfig`
  **and** the weights. The complete scoring parameterization.

### Shapes

Per rule (rename `Params` → `RuleConfig`, class attr `RuleConfig`):
```python
@dataclass(frozen=True)
class RuleConfig:
    param_budget: int = 2
    slope: float = 25.0
    violation_threshold: int = 4

class FewParameters:
    RuleConfig = RuleConfig
    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult: ...
```

Master (in `config.py`):
```python
@dataclass(frozen=True)
class CommandmentsConfig:
    configs: dict[int, object]      # number -> that rule's RuleConfig
    weights: dict[int, int]         # number -> relative importance

    def config_for(self, number: int): ...      # configs[number] or the rule's default
    def weight_for(self, number: int) -> int: ...
    def with_config(self, number, rule_config) -> "CommandmentsConfig": ...   # immutable update
    def with_weight(self, number, weight) -> "CommandmentsConfig": ...
    @classmethod
    def default(cls) -> "CommandmentsConfig": ...   # from default_rule_configs() + WEIGHTS
    def to_dict(self) -> dict: ...                   # persist a tuned set
    @classmethod
    def from_dict(cls, data: dict) -> "CommandmentsConfig": ...   # reconstruct via registry
```

`Config` gains `commandments: CommandmentsConfig = field(default_factory=CommandmentsConfig.default)` and drops `rule_params`. The engine reads
`config.commandments.config_for(number)` into `evaluate`, and `_weighted_score`
reads `config.commandments.weight_for(r.number)` (default == old `WEIGHTS`, so
behaviour-preserving).

### Calibration scaffolding (Phase 2b — skeleton only, per user)

`evals/calibrate.py` — structure but NOT the optimiser yet:
- Load `evals/corpus/comparison.json` (Moses + Judge per solution).
- `agreement(pairs) -> {spearman, mean_abs_gap}` — the objective to later minimise.
- `report_baseline(corpus)` — prints current agreement per question + overall
  (works today; this is the "measure" step).
- `optimize(...)` — a clearly-marked stub returning the default `CommandmentsConfig`
  unchanged, with a docstring/TODO describing the intended search over
  `CommandmentsConfig` once the corpus is larger.
- `main(argv)` runs `report_baseline`. The real search lands after corpus scale-up.

## User Stories

1. As a calibrator, I want one `CommandmentsConfig` object holding all rule configs
   and weights, so I can tune and serialize the entire scoring in one place.
2. As a developer, I want per-rule knobs named `RuleConfig` and the master named
   `CommandmentsConfig`, so the vocabulary matches the domain.
3. As a calibrator, I want `to_dict`/`from_dict` so a tuned config persists to disk
   and reloads.
4. As a user, I want `moses judge` to behave identically after the rename/restructure
   (behaviour-preserving).

## Implementation Decisions

- **Rename `Params` → `RuleConfig`** across all 21 rules (class, class attr, the
  `evaluate` parameter name `params` → `config`).
- **`CommandmentsConfig` lives in `config.py`**; its `default()`/`from_dict` use the
  commandments registry via a lazy import (same cycle-avoidance as today).
- **`default_rule_params()` → `default_rule_configs()`** in `commandments/__init__.py`.
- **Weights move into the master** as `weights: dict[int,int]`, defaulting to
  `WEIGHTS`; `_weighted_score` reads `config.commandments.weight_for(...)`. The
  module-level `WEIGHTS` stays as the canonical default source (and keeps its
  `sum==100` assert).
- **Deep module:** `CommandmentsConfig` hides the configs/weights wiring behind
  `config_for`/`weight_for`/`with_*`; the engine and calibration talk to it, not to
  raw dicts.
- **Behaviour preservation is the acceptance gate** (corpus `moses_scores.json`
  byte-identical; full suite green; self-host grade unchanged).
- Calibration optimiser is **scaffolding only** this iteration.

## Testing Decisions

- Behaviour-preservation gate after the refactor (corpus byte-identical, suite green).
- `CommandmentsConfig` unit tests: `default()` covers all implemented rules;
  `config_for`/`weight_for` return defaults; `with_config`/`with_weight` are
  immutable updates; `to_dict`→`from_dict` round-trips to an equal object.
- Engine test: a `Config` whose `commandments` overrides one rule's `RuleConfig`
  (and one weight) is actually applied in a full `run`.
- `evals/calibrate.py`: unit-test `agreement()` (known pairs → known spearman/gap);
  `report_baseline` smoke over the existing corpus.

## Out of Scope

- The real calibration optimiser/search (Phase 2b proper) — scaffolding only now.
- Scaling the corpus to all 15 (the next effort, "(2)").
- Renaming the run-level `Config` (stays as-is).
- Per-question config sets.
