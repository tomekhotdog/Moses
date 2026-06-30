# C30 + C4 — Over-engineering Rules Design

## Research

The calibration corpus exposed Moses's biggest blind spot: it is **blind to global
over-engineering**. Over-engineered solutions (e.g. 2024_q10 `online_1`: a threading
decorator + dual recursion/loop implementations; 2022_q11 `online_1`: a nested-lambda
+ `eval` one-liner) score A on Moses because every method is *locally* tidy (low
C11/C12/C13/C14), while the readability-focused judge rates them low. The rules that
would catch this — C4 (layers), C8 (strategic-vs-tactical), C30 (pattern parsimony)
— are all unimplemented.

### Overlap analysis (which existing rules already cover adjacent ground)

| Existing rule | Measures | Gap left for new rule |
|---|---|---|
| **C3 No pass-through** (`c03_pass_through.py`) | a single method whose body forwards args to `obj.method(...)` with exact param match | C3 is per-method prevalence; **C4** is per-*class* ("this whole layer adds no abstraction") — C3 structurally can't see a wrapper class as a layer. |
| **C1 deep modules** | LOC/API ratio per file | doesn't count abstraction-machinery constructs or single-impl abstractions |
| **C29 composition** | mean inheritance depth | a 1-subclass ABC has depth 1 → invisible to C29 but is the prime C30 smell |
| **C31 WMC** | Σ cyclomatic per class | rewards tiny machinery classes (low WMC) — C30 must counter this |
| **C21 cohesion** | LCOM4 | a 1-method strategy class is perfectly cohesive yet is the C30 smell |
| **C17/C18/C16/C25/C12** | dead code / empty catch / dup / magic / complexity | these collectively own ~all of **C8**'s deterministic signal |

**Conclusions:** C30 has the cleanest distinct territory (no rule counts abstraction
machinery). C4's genuine gap beyond C3 is *delegation-wrapper classes*. **C8 is
deferred** — every robust deterministic signal it could use is already owned by
C17/C18/C16/C25/C12; the only non-overlapping signal (TODO/HACK markers) measures
self-reported debt, not design quality, and is trivially gamed. Forcing C8 would add
a weak, double-counting rule.

Rule shape (from existing rules): `evaluate(self, codebase, config: RuleConfig) ->
CommandmentResult`, compute a ratio `M`, `clamp(100 − slope·M)`, register in
`commandments/__init__.py` `ALL_COMMANDMENTS` (the `default_rule_configs()` registry
and `CommandmentsConfig` pick them up automatically). Helpers in `_ast_helpers.py`:
`iter_classes`, `methods_of`, `is_dunder`, `parse_file`. C29 has reusable base-name
resolution; C3 has reusable pass-through detection.

## Problem Statement

Moses cannot see when code is over-engineered for its problem — needless abstraction
machinery, single-implementation indirection, and thin delegation layers. This caps
how well its Score can ever track a readability/complexity-control judge. Implement
the two rules with genuine distinct deterministic signal: C30 and C4.

## Solution

### C30 — Pattern parsimony (over-engineering)

Over-engineered-class ratio, blending two per-class signals (class flagged if either):
- **Lone abstraction**: class is a *nominal* abstraction (inherits `ABC`, uses
  `ABCMeta` metaclass, or has an `@abstractmethod`) with **≤1 in-codebase subclass**.
  (Bare `Protocol` used only for typing is NOT counted — good structural-typing
  practice.)
- **Tiny class**: ≤1 non-dunder method (or only `__init__`).

`ratio = over_engineered / eligible_classes`; `score = clamp(100 − slope·ratio)`.
**Exclusions (mandatory — avoids fighting C27 which rewards small data types):**
`@dataclass`, `Enum`/`IntEnum`/`StrEnum`, `NamedTuple`, `Exception` subclasses,
typing-only `Protocol`. **`not_measured`** when there are no eligible classes
(functional code is correctly out of C30's scope).

### C4 — Layers add abstraction (delegation wrappers)

Delegation-wrapper-class ratio. A class is a wrapper if it stores an injected object
(`self.x = <param>` in `__init__`) **and ≥3 public methods forward to that same
`self.x` with the identical method name** (≥60% of public methods). Same-name
requirement spares genuine Adapters/Facades that transform the interface.
`score = clamp(100 − slope·ratio)`; `not_measured` when no classes.

C4 vs C3: C3 = per-method prevalence of pass-throughs; C4 = per-class "this layer
adds no abstraction". Different granularities; correlation is handled by calibration
weights.

## User Stories

1. As a reviewer, I want Moses to penalise needless abstraction machinery
   (single-impl ABCs, swarms of tiny classes), so over-engineered code stops scoring A.
2. As a reviewer, I want delegation-wrapper layers flagged, so thin pass-through
   classes that add no abstraction are visible.
3. As the calibrator, I want these validated against the corpus's over-engineered
   solutions before they count, so a misfiring rule doesn't degrade the Score.

## Implementation Decisions

- New modules `commandments/c30_pattern_parsimony.py`, `commandments/c04_layers.py`,
  each with a frozen `RuleConfig` and `evaluate(self, codebase, config)`; registered
  in `ALL_COMMANDMENTS`. `default_rule_configs()`/`CommandmentsConfig` pick them up
  with no extra wiring.
- C30 reuses C29's base-name resolution for the subclass map; C4 reuses C3's
  pass-through detection idea (single forwarding call to `self.x.<same-name>(...)`).
- Shared exclusion helpers (is-dataclass / is-enum / is-namedtuple / is-exception /
  is-protocol) likely added to `_ast_helpers.py` for reuse.
- **Kept OUT of `MVP_COMMANDMENTS` initially.** Validate on the corpus (score with
  them enabled; confirm they fire on the known over-engineered solutions). Only then
  add to MVP and re-run `evals/calibrate.py` so weights reflect their contribution.
- **Deep module:** each rule exposes a small `evaluate` interface; the AST
  classification (abstraction detection, exclusion logic, wrapper detection) stays
  inside.
- C8 deferred (stays `not_measured`) — documented as deliberate, not an oversight.

## Testing Decisions

- Per-rule fixtures + unit tests asserting measured behaviour:
  - C30: a fixture with a single-impl ABC and a swarm of tiny classes scores low; a
    dataclass/Enum-heavy domain model is NOT penalised (the C27 anti-fight check);
    functional code → `not_measured`.
  - C4: a delegation-wrapper class (≥3 same-name forwarders) scores low; an Adapter
    that renames/transforms methods is NOT flagged; no-class code → `not_measured`.
- Behaviour-preservation for the rest: full suite green; existing corpus
  `moses_scores.json` for default (MVP) runs unchanged (the new rules aren't in MVP
  yet, so default scoring is identical).
- Validation (not a unit test): re-score the corpus with C4+C30 enabled and report
  whether they fire on the over-engineered solutions; this gates MVP promotion.

## Out of Scope

- **C8 strategic-vs-tactical** — deferred (too fuzzy / double-counts existing rules).
- **Promoting to MVP + recalibration** — a separate step after validation.
- Re-export-module detection for C4 (gutted by the `__init__.py` exclusion) and
  single-caller call-graph chains (fragile by-name) — rejected per research.

## Validation results (2026-06-26)

Scored the corpus with C4+C30 enabled (on top of MVP) and checked the known
over-engineered solutions vs clean controls:

| Solution | Judge | C30 | C4 | Note |
|---|---|---|---|---|
| 2024_q10/online_1 | 42 | **25** | 100 | over-eng (threading + dual impl) — C30 flags |
| 2024_q21/online_1 | 35 | **0** | 100 | over-eng (animation cruft) — C30 flags |
| 2023_q11/tomek | 47 | **0** | 100 | over-eng (Universe/Pair classes) — C30 flags |
| 2022_q11/online_1 | 7 | not_measured | not_measured | functional lambda+eval blob (no classes — C30 out of scope) |
| 2024_q10/synth_clean | 93 | 100 | 100 | clean control — not flagged |
| 2024_q12/synth_clean | 92 | not_measured | 100 | clean control — not flagged |
| 2023_q5/synth_clean | 95 | not_measured | 100 | clean control — not flagged |

**Findings:**
- **C30 is a strong, clean signal** — penalises class-based over-engineering (0–25)
  while leaving clean code at 100/not_measured (no false positives). **Recommend
  promoting C30 to MVP and re-calibrating** so its weight is set against the corpus.
- **C4 fired on nothing** — AoC solutions contain no delegation-wrapper classes. It
  is correct (no false positives) but inert on this corpus, and a near-always-100
  rule would *dilute* the Score (more leniency). **Recommend keeping C4 out of MVP**
  until we have codebases that actually contain wrappers.
- **Gap:** C30 is class-scoped, so functional over-engineering (2022_q11's lambda
  blob, judge 7) is invisible to it — that belongs to C12 (cognitive complexity).

## Recalibration after promoting C30 to MVP (2026-06-30)

Added C30 to `MVP_COMMANDMENTS`, re-scored the corpus, re-ran the split-aware
optimizer, and applied the tuned gamma + renormalized integer weights to
`config.py`. C4 stayed out of MVP (inert on this corpus).

Mean per-question Spearman (Moses vs Judge):

| Split | pre-C30 tuned | C30-in-MVP tuned | applied (int weights) |
|---|---|---|---|
| train | 0.507 | 0.651 | 0.637 |
| validation | 0.343 | 0.583 | 0.583 |
| test | 0.778 | 0.804 | 0.804 |

Validation rose the most (0.34 → 0.58) — the gain generalizes, it is not train
overfitting. Optimizer moves applied: C30 2→7, C12 10→16 (up); C16 12→5, C27 4→1,
C1 3→2 (down); gamma stayed 0.75. Integer renormalization (largest-remainder, no
rule zeroed) costs only ~0.014 on train, 0 on val/test. Self-host 83.2 (A); C30
measured at 100 on Moses's own code (no false positive). Full suite green
(171 passed, 1 skipped).
