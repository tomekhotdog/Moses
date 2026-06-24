# Explicit Rule-Parameter Config (Phase 2a) Design

## Research

### The calibration surface (from rule inventory)

Every implemented rule maps a metric to a score via a tunable curve. Inventory:

- **WEIGHTS** (`config.py:11`) — 22 integer weights summing to 100; applied in
  `_weighted_score` (`engine.py:42`) as `Σ(wᵢ·Sᵢ)/Σwᵢ` over enabled+measured. An
  *aggregation* knob, not used inside rule eval.
- **Per-rule curve knobs (~46)** — slopes `K`, budgets/thresholds `B`, floor/ceil
  ramps, ratios. Some are named module constants (e.g. `PARAM_BUDGET=2`), but many
  slopes are **hardcoded inline** in the formula (e.g. c13 `clamp(100 - 25*max(0,
  m-2))` — the `25` is unnamed). Curve-shape taxonomy:
  - Linear penalty `100 - K·max(0, M-B)` — rules 5,6,11,13,14,17,21,22,23,24,25,29
  - Ratio `100·M` / ratio-with-target `100·M/T` — rules 20, 27
  - Floor/ceil ramp `100·(CEIL-M)/(CEIL-FLOOR)` — rules 2, 31
  - Large-K near-binary `100 - K·M` — rules 3,15,16
  - Composite weighted — rule 12 (`0.7·S_cog + 0.3·S_cyc`)
  - Saturating multiplier `K·M` — rule 1
- **21 of 22 rules have ≥1 continuous knob**; only #20 (mutation, `100·kill_rate`)
  is knob-free.

### Current threading constraint (being retired)

`evaluate(self, codebase)` receives **no config** (`engine.py:118` calls
`cmd.evaluate(codebase)` flat). Tunables are module constants; calibration cannot
reach them. The deferred-config decision in `lessons.md` recorded this; this design
supersedes it.

### Data already captured

`evals/corpus/comparison.json` stores per-solution per-commandment
`score_contribution` (weights recomputable offline) but NOT per-rule metrics — so
curve-knob calibration requires re-running Moses with overridden params, which is
exactly what this config structure enables.

## Problem Statement

Moses' rule parameters are scattered module constants and inline magic numbers that
cannot be set from outside. The pilot (Phase 1) showed Moses is systematically more
lenient than the judge, and the leniency lives in the curves. Before any
calibration can tune those curves, the parameters must become **explicit, typed,
required config threaded into each rule's eval logic** — first-class data, not
hidden constants.

## Solution

Give every implemented rule a frozen `Params` dataclass holding all its tunables
(including the slopes currently hardcoded inline), defaults equal to today's
values. Make `evaluate` require it. Thread it from `Config` through the engine.

### Per-rule `Params`

In each `cNN_*.py`:
```python
@dataclass(frozen=True)
class Params:
    param_budget: int = 2
    slope: float = 25.0
    violation_threshold: int = 4
```
- Holds **all** knobs for that rule — budgets, thresholds, slopes (`K`), floor/ceil,
  ratios — extracting inline magic numbers so the curve is fully tunable.
- Defaults = current values ⇒ behaviour-preserving.
- Parameter-free rules (#20) still define an (empty) `Params` for a uniform
  interface.

### Required at the eval boundary

```python
def evaluate(self, codebase, params: Params) -> CommandmentResult:
    ... params.slope ...   # no module constants, no inline magic
```

### Threading & defaults (defaulted at the top)

- `default_rule_params() -> dict[int, Params]` in `commandments/__init__.py` (it
  already imports every rule — no import cycle; rule `Params` import nothing from
  `config`). Maps rule number → that rule's default `Params`.
- `Config` gains `rule_params: dict[int, Params]` with `default_factory =
  default_rule_params`. The engine passes `config.rule_params[number]` into
  `evaluate`. `engine.run(root)` with no config still works (defaults fill in).

### Weights stay separate

Weights are an aggregation knob applied in `_weighted_score`, not used inside rule
eval. They remain in `config.py`/`WEIGHTS` and are already overridable. Not folded
into per-rule `Params`.

## User Stories

1. As a calibrator, I want every rule's curve knobs to be explicit typed config I
   can set, so I can later tune them to track the judge.
2. As a maintainer, I want each rule's parameters co-located with the rule and
   type-checked, so the knobs are discoverable and safe to change.
3. As a user, I want `moses judge` to behave identically after the refactor, so the
   structure change is provably free of scoring drift.

## Implementation Decisions

- **Per-rule frozen `Params`** (the chosen shape): typed, defaults co-located,
  matches Moses' own "data over primitives" ethos. A central registry
  (`default_rule_params`) is the single settable surface; a flat view for
  calibration optimization is built later on top.
- **Required param in `evaluate`** — explicit, not an optional override; the engine
  always supplies one (override or default).
- **Extract inline slopes**, not just named constants — otherwise curves stay
  un-tunable and the whole exercise is moot.
- **Behaviour preservation is the acceptance gate** (see Testing).
- **Deep module:** `default_rule_params()` + `Config.rule_params` + per-rule
  `Params` hide all wiring; rules read only their own typed params.
- Supersedes the `lessons.md` "rules cannot read Config" decision.

## Testing Decisions

- **Behaviour-preservation gate:** after the refactor, the full existing suite
  passes unchanged AND re-running `evals/corpus_score.py` yields byte-identical
  `moses_scores.json` for the pilot corpus (defaults == old values). This is the
  primary correctness proof of the mechanical migration.
- **New per-rule test:** for a representative sample of rules, overriding a knob
  moves the score in the expected direction (e.g. lower c27 `target_ratio` → higher
  C27 score; smaller c13 `param_budget` → lower score on a wide-param fixture).
- **Engine threading test:** a `Config` with an overridden `rule_params[N]` is
  actually applied to rule N's result in a full `run`.
- **Registry test:** `default_rule_params()` returns a `Params` for every
  implemented rule number, and each rule's `evaluate` accepts its `Params`.

## Out of Scope

- The calibration optimizer/harness and any parameter **value** changes — this is
  purely structure; defaults are unchanged.
- Weight-fitting / weight calibration.
- Per-question parameter sets (global params only).
- Threading config for non-scoring needs (mutmut/jscpd paths) — possible later on
  the same mechanism, not done here.
