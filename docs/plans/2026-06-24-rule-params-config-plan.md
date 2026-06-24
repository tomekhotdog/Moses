# Explicit Rule-Parameter Config (Phase 2a) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use tomek-superpowers:build to implement this plan task-by-task.

**Goal:** Make every rule's tunable knobs an explicit frozen `Params` dataclass, threaded into `evaluate` from `Config.rule_params`, with defaults equal to today's values (behaviour-preserving).
**Architecture:** Each `cNN_*.py` defines `@dataclass(frozen=True) class Params` (all budgets/thresholds/slopes, incl. ones formerly hardcoded inline). `evaluate(self, codebase, params=None)` reads from it (`params = params if params is not None else Params()`). A `default_rule_params()` registry + `Config.rule_params` thread overrides through the engine. A final task removes the `=None` to make params required.
**Tech Stack:** Python stdlib dataclasses; `moses` engine; pytest.
**Design:** `docs/plans/2026-06-24-rule-params-config-design.md`

Work on `main` (user preference). Tests: `uv run pytest` (sandbox disabled, per `docs/lessons.md`).

## Staging strategy (keeps the suite green at every commit)

1. Rules migrate to `evaluate(self, codebase, params=None)` with an internal default — the engine still calls `evaluate(codebase)` and stays valid (Tasks 1–3).
2. Only after ALL rules accept a param do we thread the engine (Task 4).
3. Then tighten to required (`params: Params`, no default) (Task 5).

## The behaviour-preservation gate (run after every task)

```
uv run pytest -q                                   # full suite green
uv run python evals/corpus_score.py --corpus evals/corpus --year 2024
git diff --stat evals/corpus/moses_scores.json     # MUST be empty (byte-identical scores)
```
If `moses_scores.json` changes, a default was not preserved — fix before committing.

## Per-rule knob table (the migration spec — defaults = current values)

| # | Params fields (name=default) | Current curve to preserve |
|---|---|---|
| 1 | `multiplier=10.0` | `clamp(multiplier * M)` |
| 2 | `floor=14.0, ceil=20.0` | ramp: `100 if M<=floor; 100*(ceil-M)/(ceil-floor) if M<ceil; else 0` |
| 3 | `slope=1000.0` | `clamp(100 - slope * M)` |
| 5 | `budget=1.0, slope=20.0` | `clamp(100 - slope*max(0, M-budget))` |
| 6 | `slope=50.0` | `clamp(100 - slope * M)` |
| 11 | `loc_budget=50, slope=2.0, violation_threshold=50` | `clamp(100 - slope*max(0, p95-loc_budget))` |
| 12 | `complexity_budget=5, slope=10.0, cog_weight=0.7, cyc_weight=0.3, violation_threshold=10` | composite: each `clamp(100 - slope*max(0, M-complexity_budget))`, combined `cog_weight*S_cog + cyc_weight*S_cyc` |
| 13 | `param_budget=2, slope=25.0, violation_threshold=4` | `clamp(100 - slope*max(0, M-param_budget))` |
| 14 | `depth_budget=2, slope=25.0, violation_threshold=3` | `clamp(100 - slope*max(0, p95-depth_budget))` |
| 15 | `slope=500.0` | `clamp(100 - slope * M)` |
| 16 | `min_block_tokens=50, slope=1000.0` | `clamp(100 - slope * M)` (min_block_tokens gates detection) |
| 17 | `min_run=2, slope=20.0` | `clamp(100 - slope * M)` (min_run gates detection) |
| 18 | `slope=100.0` | `clamp(100 - slope * M)` |
| 20 | (empty `Params`) | `clamp(100 * kill_rate)` — no knob |
| 21 | `budget=1.0, slope=50.0` | `clamp(100 - slope*max(0, M-budget))` |
| 22 | `budget=1.0, slope=50.0` | `clamp(100 - slope*max(0, M-budget))` |
| 23 | `scope_budget=0.3, slope=200.0` | `clamp(100 - slope*max(0, M-scope_budget))` |
| 24 | `slope=200.0` | `clamp(100 - slope * M)` |
| 25 | `allowed=frozenset({0, 1, -1}), slope=2.0` | `clamp(100 - slope * M)` (allowed exempts literals) |
| 27 | `target_ratio=0.6, violation_threshold=0.5` | `clamp(100 * DSR / target_ratio)` |
| 29 | `budget=1.0, slope=50.0` | `clamp(100 - slope*max(0, M-budget))` |
| 31 | `floor=20.0, ceil=60.0` | ramp like #2 |

> Note: this is a large mechanical refactor. The behaviour-preservation gate (corpus scores byte-identical + full suite green) is the correctness proof per rule; read each rule's current source before editing and keep the formula numerically identical when defaults are used.

---

### Task 1: Pattern tracer on C13 (optional param, engine unchanged)
**Depends on:** none

**Files:**
- Modify: `src/moses/commandments/c13_few_parameters.py`
- Test: `tests/unit/test_rule_params.py`

**Step 1: Write the failing test**
```python
"""Rule Params: explicit, typed knobs threaded into evaluate (behaviour-preserving)."""

from __future__ import annotations

from moses.commandments.c13_few_parameters import FewParameters, Params


def test_c13_default_params_unchanged(bad_codebase):
    # Calling with no params must equal calling with the default Params().
    a = FewParameters().evaluate(bad_codebase)
    b = FewParameters().evaluate(bad_codebase, Params())
    assert a.score_contribution == b.score_contribution
    assert a.metric == b.metric


def test_c13_override_param_budget_changes_score(bad_codebase):
    # A larger param budget is more lenient -> score should not decrease;
    # a smaller budget is stricter -> score should not increase.
    strict = FewParameters().evaluate(bad_codebase, Params(param_budget=0))
    lenient = FewParameters().evaluate(bad_codebase, Params(param_budget=10))
    assert lenient.score_contribution >= strict.score_contribution


def test_c13_override_slope_changes_score(bad_codebase):
    gentle = FewParameters().evaluate(bad_codebase, Params(slope=1.0))
    harsh = FewParameters().evaluate(bad_codebase, Params(slope=99.0))
    assert gentle.score_contribution >= harsh.score_contribution
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_rule_params.py -q`
Expected: FAIL (cannot import `Params` from c13)

**Step 3: Implement** — read the current `c13_few_parameters.py`, then refactor to:
```python
"""Commandment 13 — Few parameters.

Metric: mean param count across all functions, excluding self/cls and dunders.
Curve:  100 − slope·max(0, M − param_budget).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_dunder, iter_functions, mean, param_names

NUMBER = 13
NAME = "Few parameters"


@dataclass(frozen=True)
class Params:
    param_budget: int = 2
    slope: float = 25.0
    violation_threshold: int = 4


class FewParameters:
    number = NUMBER
    name = NAME
    Params = Params

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, params: Params | None = None) -> CommandmentResult:
        params = params if params is not None else Params()
        counts = []
        violations = []
        for f in iter_functions(codebase):
            if is_dunder(f.name):
                continue
            n = len(param_names(f.node, skip_self=True))
            counts.append(n)
            if n >= params.violation_threshold:
                violations.append(
                    {
                        "file": f.file.relpath,
                        "line": f.lineno,
                        "function": f.qualname or f.name,
                        "params": n,
                    }
                )

        if not counts:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = mean(counts)
        score = clamp(100 - params.slope * max(0, m - params.param_budget))
        violations.sort(key=lambda v: v["params"], reverse=True)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 2),
            score_contribution=score,
            status="measured",
            detail={"mean_params": round(m, 2), "function_count": len(counts)},
            violations=violations[:50],
        )
```
Note: expose `Params = Params` as a class attribute on the rule so the registry (Task 4) can build defaults uniformly.

**Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_rule_params.py -q` → PASS.
Then the behaviour-preservation gate: `uv run pytest -q` (green) and confirm `evals/corpus/moses_scores.json` is unchanged after re-score (C13 default == old).

**Step 5: Commit**
```bash
git add src/moses/commandments/c13_few_parameters.py tests/unit/test_rule_params.py
git commit -m "refactor(rules): C13 explicit Params (tracer, behaviour-preserving)"
```

---

### Task 2: Migrate the linear-penalty + simple rules
**Depends on:** Task 1

Apply the SAME pattern (add frozen `Params`, `Params = Params` class attr, `evaluate(self, codebase, params=None)` with internal default, formula reads `params.*`) to these rules, using the knob table above:
**5, 6, 11, 14, 15, 17, 18, 21, 22, 23, 24, 25, 29.**

For each: read the current source, extract every constant AND inline magic number into `Params` with the current value as default, rewrite the curve to use `params.*`, keep numerically identical at defaults.

**Verification (the gate):**
- `uv run pytest -q` → green.
- Re-run `uv run python evals/corpus_score.py --corpus evals/corpus --year 2024`; `git diff --stat evals/corpus/moses_scores.json` → EMPTY (defaults preserved).
- Add to `tests/unit/test_rule_params.py` one override test per archetype not already covered (e.g. a floor/ceil rule is in Task 3; here cover a `slope`-only rule like C6 and a `budget`+`slope` rule like C21): assert a stricter knob never raises the score on `bad_codebase`.

**Commit:**
```bash
git add src/moses/commandments/c0{5,6}*.py src/moses/commandments/c1{1,4,5,7,8}*.py src/moses/commandments/c2{1,2,3,4,5}*.py src/moses/commandments/c29*.py tests/unit/test_rule_params.py
git commit -m "refactor(rules): explicit Params for linear-penalty + simple rules"
```

---

### Task 3: Migrate the remaining curve archetypes
**Depends on:** Task 2

Apply the pattern to the structurally different rules using the table:
- **1** (saturating multiplier), **2** & **31** (floor/ceil ramp), **3** & **16** (large-K), **12** (composite weights), **20** (empty Params), **27** (ratio-with-target — note C27 already has `TARGET_RATIO`/`VIOLATION_THRESHOLD` module constants; move them into `Params(target_ratio=0.6, violation_threshold=0.5)` and update its existing tests if they import the constants).

For #20, define an empty `@dataclass(frozen=True) class Params:` and `evaluate(self, codebase, params=None)` that accepts and ignores it (keep the `Params = Params` attr).

**Verification (the gate):**
- `uv run pytest -q` → green (update any C27 test that referenced the old module constants).
- `moses_scores.json` byte-identical after re-score.
- Add override tests: a floor/ceil rule (C2: tightening `ceil` lowers score on a high-CBO fixture), and C27 (lower `target_ratio` raises score on `well_modelled`).

**Commit:**
```bash
git add src/moses/commandments/c01*.py src/moses/commandments/c02*.py src/moses/commandments/c03*.py src/moses/commandments/c12*.py src/moses/commandments/c16*.py src/moses/commandments/c20*.py src/moses/commandments/c27*.py src/moses/commandments/c31*.py tests/unit/
git commit -m "refactor(rules): explicit Params for ramp/composite/ratio rules"
```

---

### Task 4: Registry + Config.rule_params + engine threading
**Depends on:** Task 3 (all rules now accept a param)

**Files:**
- Modify: `src/moses/commandments/__init__.py` (add `default_rule_params`)
- Modify: `src/moses/config.py` (add `rule_params` field)
- Modify: `src/moses/engine.py` (thread params into `cmd.evaluate`)
- Test: `tests/unit/test_rule_params.py` (engine-threading test)

**Step 1: Write the failing test** (append):
```python
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
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_rule_params.py -q` → FAIL (no `default_rule_params`, `Config.rule_params`).

**Step 3: Implement**
In `src/moses/commandments/__init__.py`, after `ALL_COMMANDMENTS`:
```python
def default_rule_params() -> dict:
    """Map each implemented rule number to a fresh default Params instance."""
    return {cmd.number: cmd.Params() for cmd in ALL_COMMANDMENTS}
```

In `src/moses/config.py`, add to `Config` (and import the registry lazily to avoid a cycle):
```python
    rule_params: dict = field(default_factory=lambda: _default_rule_params())
```
with a module-level helper near the top:
```python
def _default_rule_params() -> dict:
    from .commandments import default_rule_params

    return default_rule_params()
```
Ensure `with_overrides`/`from_file` carry `rule_params` through (preserve existing instance: pass `rule_params=self.rule_params` in `with_overrides`'s returned Config).

In `src/moses/engine.py`, change the call site (`engine.py:118`):
```python
        params = config.rule_params.get(number)
        try:
            result = cmd.evaluate(codebase, params)
```
(`params` is None for any rule missing from the dict — rules still default internally.)

**Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_rule_params.py -q` → PASS. Then the gate: `uv run pytest -q` green AND `moses_scores.json` byte-identical after re-score (default rule_params == old behaviour).

**Step 5: Commit**
```bash
git add src/moses/commandments/__init__.py src/moses/config.py src/moses/engine.py tests/unit/test_rule_params.py
git commit -m "feat(config): thread rule_params through engine into evaluate"
```

---

### Task 5: Tighten params to required
**Depends on:** Task 4

Now the engine always supplies a `Params` (override or, via `default_rule_params`, a default). Make the param **required** per the design: in every migrated rule change `def evaluate(self, codebase, params: Params | None = None)` → `def evaluate(self, codebase, params: Params)` and drop the `params = params if params is not None else Params()` line.

BUT the engine's `config.rule_params.get(number)` could return None for an enabled-but-not-implemented number — it won't, because only `ALL_COMMANDMENTS` (implemented) rules are invoked and all are in the registry. Confirm by making the engine pass `config.rule_params[number]` (KeyError would be a real bug) OR keep `.get` and assert non-None before calling. Use:
```python
        params = config.rule_params.get(number)
        if params is None:
            params = cmd.Params()
        result = cmd.evaluate(codebase, params)
```
so a custom `Config` with a partial `rule_params` dict still works (defaults fill in), while rule signatures stay required.

Update the Task-1 behaviour test `test_c13_default_params_unchanged` — `evaluate(bad_codebase)` no longer valid; replace the no-arg call with `evaluate(bad_codebase, Params())` (the two-call equality test becomes a single explicit-Params smoke; keep the override tests).

**Verification (the gate):**
- `uv run pytest -q` → green.
- `moses_scores.json` byte-identical after re-score.
- `uv run moses judge . --exclude 'tests/fixtures/*'` still exits 0, grade unchanged.

**Commit:**
```bash
git add src/moses/commandments tests/unit/test_rule_params.py src/moses/engine.py
git commit -m "refactor(rules): make Params required at the evaluate boundary"
```

---

## Review
- [ ] Code review requested (mechanism: registry/Config/engine; spot-check 3 rule migrations)
- [ ] All feedback addressed
- [ ] Final verification passed (`uv run pytest` green; `moses_scores.json` byte-identical to pre-refactor; `moses judge .` grade unchanged)
