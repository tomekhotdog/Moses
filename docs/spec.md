# Moses — Specification

Moses is a **code quality oracle for Python**. It reads a source tree, judges it
against 31 **Commandments** distilled from Ousterhout (*A Philosophy of Software
Design*), Martin (*Clean Code*), McConnell (*Code Complete*), and the GoF, and
emits a **Verdict**: a Score in [0, 100], a Grade in A–F, a ranked list of
Hotspots, machine-readable JSON, and an HTML report.

The scorer is **pure Python plus radon** — no LLM, no network, fully
deterministic. An LLM only appears in the optional autonomous *loop*, where it
plays the role of the developer making improvements; Moses itself remains the
impartial judge.

## Pipeline

```
load_codebase(root)            # SourceFile list, ignoring vendored/junk dirs
        │
        ▼
engine.run(root, config)       # iterate all 31 Commandments
        │   per-rule try/except → status="error" on failure
        ▼
Verdict(score, grade, commandments[], hotspots[], overview, meta)
        │
        ├── report.terminal.render_terminal(verdict)
        ├── report.html.render_html(verdict)
        └── verdict.to_dict()  → JSON
```

## Scoring

Each Commandment maps its Metric to a `score_contribution` in [0, 100] via a
tunable curve whose knobs (budgets, thresholds, slopes) live in an explicit frozen
**RuleConfig** dataclass on the rule, threaded into `evaluate(codebase, config)`.
The master **CommandmentsConfig** (`Config.commandments`) owns every rule's
RuleConfig and the Weights — the complete, serializable scoring parameterization.
The overall Score is a weighted mean over the rules that are **both enabled and
measured**:

```
Q = Σ (wᵢ · Sᵢ) / Σ wᵢ      for i in enabled, measured
```

Key invariant: **disabling a rule never pads the Score with a free 100.** A
disabled or `not_measured` rule is simply excluded from both numerator and
denominator. This means turning rules off cannot inflate the Score.

### Grade thresholds

| Grade | Score |
|-------|-------|
| A | ≥ 80 |
| B | ≥ 65 |
| C | ≥ 50 |
| D | ≥ 35 |
| E | ≥ 20 |
| F | < 20 |

### Status values

- `measured` — the rule ran and produced a Score that counts.
- `not_measured` — the rule is unimplemented or disabled; excluded from the Score.
- `error` — the rule raised; downgraded to status `error` so one bad rule never
  crashes the run. It does not count toward the Score.
- `skipped` — reserved for rules deliberately bypassed for a run.

## The Verdict shape

```jsonc
{
  "schema_version": 1,
  "score": 64.9,
  "grade": "C",
  "commandments": [
    {
      "number": 3,
      "name": "No pass-through methods",
      "weight": 2,
      "metric": 0.091,
      "score_contribution": 9.09,
      "status": "measured",
      "detail": { "pass_through": 2, "total": 22 },
      "violations": [ { "file": "...", "line": 126, "function": "SomeBag.delegate" } ]
    }
  ],
  "hotspots": [
    { "file": "bad.py", "severity": 41.2, "commandment_hits": { "16": 2, "25": 5 } }
  ],
  "overview": { "file_count": 1, "loc": 210, "non_blank_loc": 168 },
  "meta": { "tool_version": "0.1.0", "timestamp": "...", "commit": "...", "platform": "...", "deep": false }
}
```

## CLI surface

```
moses judge <path> [--config f] [--enable N] [--disable N] [--exclude glob]
                   [--json out.json] [--html out.html] [--deep] [--quiet]
moses prompt <N>                       # curated refactoring brief for Commandment N
moses loop init <repo> [--in-place] [--target-path src/] [--branch b]
moses loop run  --worktree <wt> [--engine auto|claude|codex] [--max-iterations N]
moses loop check  --worktree <wt>      # validate campaign.json
moses loop status --worktree <wt>      # terse progress summary
moses --version
```

`judge` exits `0` for grades A/B/C, `1` for D/E, `2` for F — usable as a CI gate.

## The autonomous loop (RALPH)

`moses loop` runs an autonomous improvement campaign. It is deliberately split:

- **`loop_runner.py`** (Python) sets up an isolated git worktree (or runs
  in-place), drops the loop template into `<state-dir>/`, records the baseline
  Verdict, and launches the harness.
- **`ralph.sh`** (shell) is the iteration engine: judge → hand `prompt.md` +
  `verdict.json` to a coding engine → verify the change improved the Score and
  did not raise violations → commit → append an audit record.
- **`check_invariants.py`** records each iteration into `campaign.json` and
  validates the whole trail against git history.

`campaign.json` is an append-only ledger and the single source of truth: every
iteration records the commit, Score before/after, and violation delta. Moses
guarantees **honest, monotonic improvement** — the harness reverts any change
that regresses the Score or increases violations rather than recording it.

## Calibration corpus (evals/)

Moses' rule parameters are hand-set. The **calibration corpus** exists to ground
them in evidence. It collects varied-quality Python solutions to the same
Advent-of-Code problems (`evals/corpus/`; 2024 trains, 2022/23 tests) and scores
each solution two independent ways: the deterministic **Moses Score**, and an
**LLM-as-judge** holistic code-quality % (the "Truth" proxy). Both land in one
`comparison.md` (backed by `comparison.json`) that surfaces where the oracle and
the judge diverge.

The split is deliberate: judging is agentic and independent of Moses output;
scoring (`evals/corpus_score.py`) and reporting (`evals/corpus_report.py`) are
deterministic scripts over JSON, so the corpus re-runs with one command. A later
phase tunes rule parameters until the Moses Score tracks the Judge across the
corpus — which requires a parameter-override mechanism Moses does not yet have.

## Design invariants (must always hold)

1. The scorer is pure stdlib + radon; deterministic; no network.
2. Every rule is wrapped in its own `try/except`; a raising rule becomes
   `status="error"` and never aborts the run.
3. Every `CommandmentResult` carries a `status`.
4. The Score averages over enabled, measured rules only.
5. Mutation testing (#20) is opt-in behind `--deep`; it never silently runs.
