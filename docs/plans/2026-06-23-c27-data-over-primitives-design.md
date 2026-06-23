# C27 — Data over primitives Design

## Research

### Existing rule landscape (Moses)

C27 *"Data over primitives"* (`descriptions.py:39`, attributed to *Fowler, primitive
obsession*, **weight 3**) is currently a `not_measured` placeholder — the slot
exists, no weight reshuffle is needed, and the `sum(WEIGHTS) == 100` invariant is
untouched.

The domain-modelling idea overlaps heavily with rules that already exist:

| Concept | Rule | Status |
|---|---|---|
| meaning silently encoded in primitives | **C27 Data over primitives** | `not_measured` (this work) |
| lean on the type-checker / abstractions | **C28 Program to interfaces** | `not_measured` (future) |
| classes hide implementation | **C1 Deep modules** (impl/API ratio) | implemented |
| sensibly scoped transformations | **C21 Cohesive classes** (LCOM4), **C15 CQS** | implemented |
| object–object interaction ratios | **C2 Loose coupling** (CBO) | implemented |

Conclusion: the "domain is well modelled" ambition is ~80% **C27 + C28**. This
iteration implements **C27 only**.

Rule anatomy (from `c13_few_parameters.py`, `c06_define_errors_out.py`,
`c21_cohesive_classes.py`): a rule is a class with `number`, `name`, a `weight`
property reading `WEIGHTS[NUMBER]`, and `evaluate(codebase) -> CommandmentResult`.
It walks the AST via `_ast_helpers` (`iter_functions`, `iter_classes`,
`param_names`, `is_dunder`, `is_private`, `clamp`, `mean`), accumulates a metric +
violations, and returns `not_measured` when there is nothing to measure. Each rule
is isolated by the engine's per-rule `try/except` (`engine.py:117`), and the Score
is `Σ(wᵢ·Sᵢ)/Σwᵢ` over **enabled and measured** rules only (`engine.py:42`).

`SourceFile` exposes `.text`, `.relpath`, `.is_test`, line counts; AST is parsed
on demand and memoised on the `SourceFile` instance. No type resolution, call
graph, or radon metrics are precomputed.

### External research

- **Primitive Obsession** (Fowler): representing domain concepts (money, ranges,
  ids) with raw primitives. Canonical fixes: Replace Primitive with Object,
  Introduce Parameter Object, Replace Type Code with Class.
- **Data Clumps** (Fowler): primitives that travel together and should be an
  object. Detection heuristics use clump size ≥3 (Fowler) / 3–4 (Zhang), matched
  on name+type, order-insensitive.
- **Connascence of Meaning** (connascence.io): a primitive whose *value* silently
  encodes domain meaning (status as `int`, `None` overloaded). This is C27's exact
  target. The documented fix is to raise it to Connascence of Name — i.e. a named
  type/enum. **Caveat:** CoM is not reliably auto-detectable; C27 measures
  *proxies* (primitive-typed public surface), not meaning itself.
- **Prior art:** *Primitive Enthusiasm* (Gál & Pengő, CSCS 2018) is the only
  academic relative — parameter-only, Java-only, relative (above-class-average)
  trigger. No tool (SonarQube, PMD, Sourcery) computes a domain-type ratio.
  Including **return types + attributes** and an absolute ratio is novel.
- **Threshold reality:** the literature explicitly refuses an absolute primitive
  threshold ("application, problem, and coding-guideline dependent"). Our `TARGET`
  is therefore *conventional* and calibration-pending, to be tuned by the corpus.
- **Python type signals:** `NewType`, `Enum`/`StrEnum`, dataclass/attrs/pydantic/
  `NamedTuple` are strong domain-positive signals; `Literal`/`TypedDict`/`IntEnum`
  weak-positive; bare `str/int/float/bool/bytes/None`, `Any`, and unparameterized
  `dict`/`list` are primitive/erased (mypy treats bare generics as `Any`).
  `datetime`/`date`/`Decimal`/`UUID`/`Path` are domain-positive value types.

## Problem Statement

Moses cannot currently judge whether a codebase **models its domain** or smears it
across raw primitives. A high-quality codebase expresses its public surface in
terms of *concepts* — `UserId`, `Money`, `Order` — so that meaning falls out of
the types and the type-checker enforces correctness. A low-quality one passes
`str`, `int`, and `dict[str, int]` everywhere, forcing readers to carry meaning in
their heads. C27 makes this measurable and deterministic.

## Solution

Implement C27 as a deterministic **Domain Surface Ratio (DSR)**: the mean
domain-richness of a codebase's public, annotated type surface.

### Qualifying slots (denominator)

Every **annotated** slot that is a:
- function/method **parameter** (excluding `self`/`cls`),
- function/method **return** annotation,
- class **attribute** annotation (dataclass fields, `name: T` class/instance vars),

subject to exclusions:
- **public only** — skip `_private` and `__dunder__` names,
- skip **test files** (`SourceFile.is_test`),
- skip `@property` getters and single-parameter setters,
- skip per-project `c27_exclude_paths` (e.g. `parsers/`, `io/`, numeric kernels),
- **unannotated slots are NOT scored** (per decision) but counted toward a
  reported `annotation_coverage` so the "strip types to dodge judgment" gaming
  path is visible in the Verdict.

If there are zero qualifying annotated slots, C27 returns `not_measured` (never
padded to 100; excluded from the Score).

### Per-slot domain score `s ∈ [0, 1]`

| Annotation | `s` |
|---|---|
| user-defined class, `NewType`, `Enum`/`StrEnum`, dataclass/attrs/pydantic/`NamedTuple`, `datetime`/`date`/`Decimal`/`UUID`/`Path` | **1.0** |
| `Literal[...]`, `TypedDict`, `IntEnum` | **0.5** |
| `str`/`int`/`float`/`bool`/`bytes`/`complex`/`None`, `Any`, bare `dict`/`list`/`tuple` | **0.0** |

**Containers score by their type arguments** (the key nuance):
- `list[X]` / `set[X]` / `frozenset[X]` / `Sequence[X]` / `Iterable[X]` → `score(X)`
  — a collection *of a concept* is free; one level of structural nesting costs
  nothing.
- `dict[K, V]` / `Mapping[K, V]` → `min(score(K), score(V))` — both must be
  concepts. `dict[str, int]` → 0 (primitive-keyed, primitive-valued bag = the
  classic CoM smell).
- `tuple[...]` → `min` over args; **≥2 primitive args ⇒ 0** (data clump →
  `NamedTuple`/dataclass).
- `Optional[X]` / `X | None` → `score(X)` — nullability is C6's concern, not C27's.
- `Union[A, B, ...]` (after stripping `None`) → `min` over members.

### Classification strategy

Pragmatic, **no name resolution** initially: any annotation name not in the
primitive / container / `typing`-erased denylist is treated as a concept. The
false negative — a `UserId = int` plain alias scored as a concept — is accepted;
the corpus will tell us whether intra-module alias resolution
(`NewType`, `TypeAlias`) is worth the added complexity.

### Reward tiny types explicitly

Tiny domain types are first-class:
- a `NewType('UserId', int)` or a one-field value object used in a signature
  scores a full **1.0** (use-side reward, already implied above);
- C27 additionally reports a **domain-vocabulary-density** detail —
  `domain_types_defined / kLOC` (count of `NewType`/`Enum`/dataclass/`NamedTuple`/
  class definitions per 1000 non-blank LOC) — so a codebase that *defines* a rich
  vocabulary of small types is visibly credited, even before it is fully threaded
  through every signature. This is a reported signal for explainability; the
  headline `score_contribution` remains the DSR curve.

### Curve

```
score_contribution = clamp(100 · DSR / TARGET),  TARGET = 0.6   (configurable)
```

`TARGET = 0.6` means "60% of the public surface expressed as concepts = full
marks." This is the opinionated dial and is **calibration-pending** — the
Advent-of-Code corpus (separate effort) is what tunes it. Exposed as
`c27_target_ratio`.

### Violations

Ranked worst-offenders with `file:line`:
- public functions/methods with the lowest mean slot score,
- specific smells: `dict[<primitive>, <primitive>]` mappings, primitive `tuple`
  clumps, bare `Any`/unparameterized containers in public signatures.

## User Stories

1. As a developer, I want Moses to reward expressing my public API in domain types
   (`UserId`, `Money`, `Order`) so that well-modelled code scores higher.
2. As a developer, I want `dict[str, int]`-style primitive bags and primitive
   tuple clumps flagged as hotspots so I know where to introduce a type.
3. As a developer, I want `list[Order]` to count as good while `dict[str, int]`
   counts as bad, so the metric matches how concepts actually compose.
4. As a maintainer of an under-typed codebase, I want C27 to judge only my
   annotated surface (and report annotation coverage) rather than punishing me for
   missing annotations it can't read.
5. As a project owner, I want to tune the target ratio and exclude IO/parsing/
   numeric modules so the rule doesn't punish code where primitives are the domain.

## Implementation Decisions

- **New module** `commandments/c27_data_over_primitives.py`, class
  `DataOverPrimitives`, registered in `commandments/__init__.py`'s
  `ALL_COMMANDMENTS`.
- **Deep module (Ousterhout):** the whole annotation taxonomy + container
  recursion + exclusion logic hides behind a single `score_annotation(node) ->
  float` interface plus the `evaluate` entry point. Callers see a ratio; the AST
  classification complexity stays inside.
- **New AST helpers** likely added to `_ast_helpers.py`: an annotation-node
  classifier and a "domain type definition" detector, reused by future C28.
- **Config:** add `c27_target_ratio: float = 0.6` and
  `c27_exclude_paths: list[str]` to `Config`, threaded through `from_file` and
  `with_overrides`. Keeps C27 tunable per project without code changes.
- **No name resolution** in v1 (accepted false negative on plain aliases).
- **Determinism preserved:** pure stdlib AST, no network, no LLM — Moses's
  load-bearing invariant holds.

## Testing Decisions

- New fixtures under `tests/fixtures/`:
  - `primitive_heavy/` — stringly-typed signatures, `dict[str, int]` everywhere,
    primitive tuples → should score low.
  - `well_modelled/` — `NewType`, `Enum`, dataclasses, `dict[UserId, Money]`,
    `list[Order]` → should score high.
- Unit tests assert **measured behaviour**, not a blanket bad<good (per
  `lessons.md`): in particular a direct test that `score_annotation` ranks
  `list[Order]` > `dict[str, int]` > bare `int`, and that the container rule and
  `Optional` stripping behave as specified.
- Test that unannotated slots are excluded from the denominator but counted in
  `annotation_coverage`.
- Test that `not_measured` is returned when there are no annotated public slots
  (so the Score is never padded).
- Follow the existing `test_cheap_commandments.py` parametrized pattern where it
  fits.

## Out of Scope

- **C28 Program to interfaces** and the naming rules (C9/C10) — future iterations.
- **Intra-module type-alias resolution** (`UserId = int`) — deferred; corpus will
  decide if needed.
- **The Advent-of-Code training/test/validation corpus** — its own effort. It is
  the *validation* mechanism that calibrates `TARGET` and, later, regression-tests
  every rule against labelled good/bad examples. Designed separately.
- **Easier rule on/off ergonomics** — raised in discussion; not part of this rule.
