# Moses Loop TUI — Live Status Enhancements Design

## Research

The dashboard (`moses loop watch`, shipped 2026-06-30) renders recorded campaign
state well, but the *in-flight* iteration shows only a bare "running" row: you
cannot see which phase the harness is in, how long it has been working, or watch
individual commandments move. The RALPH harness (`loop_template/ralph.sh`) already
progresses through clear phases per iteration (judge → engine → verify →
commit/revert → cooldown) and logs them, but nothing structured is exposed for a
UI to read. `campaign.json`'s `baseline` records only an aggregate score, so
per-rule movement vs baseline is not currently derivable.

## Problem

Three gaps in "knowing what the loop is doing":
1. **No live current-iteration status** — the phase, elapsed time, and this
   iteration's starting score are invisible until the iteration commits.
2. **No per-rule movement** — the breakdown shows only the current weakest six;
   you can't see every measured rule or how far each has moved from baseline.
3. **Thin iteration detail** — the current target rule isn't highlighted, and the
   diff panel shows a bare stat without the commit's intent.

## Solution

### 1. Structured live status via `status.json` (not log-scraping)

The harness writes `<state-dir>/status.json` at each phase transition — a tiny,
atomically-replaced file the reader polls. This is deterministic and robust,
unlike parsing claude's interleaved log output.

Shape:
```json
{"iteration": 4, "max_iterations": 10, "phase": "engine",
 "before_score": 84.0, "before_violations": 61, "started_at": 1719800000}
```
Phases: `judging`, `engine`, `verifying`, `committing`, `reverting`, `cooldown`,
`done`. `started_at` is the epoch when the *current phase* began (so the UI can
show elapsed). `before_score`/`before_violations` are filled once judged (null
during the initial `judging` phase).

`ralph.sh` gets a `write_status()` helper (python3 one-liner writing the JSON to
a temp file then `mv` for atomicity) called at each transition. On normal exit it
writes `phase: "done"`.

### 2. Per-rule baseline capture

`loop_runner._score_of` additionally records each measured rule's score:
`"commandments": {"16": 0.0, "12": 100.0, ...}`. This lands in `campaign.json`'s
`baseline` (and `best`) with no schema break (additive key). The reader then
diffs the latest `verdict.json` per-rule scores against the baseline map.

### 3. Reader additions (`loop_watch`)

`CampaignState` gains:
- `current: CurrentIteration | None` — `(iteration, max_iterations, phase,
  before_score, before_violations, started_at)` from `status.json`; `None` when
  absent or `phase == "done"`.
- `all_rules: tuple[RuleScore, ...]` — every measured rule from the latest
  verdict (sorted weakest-first), not just six.
- `baseline_rules: dict[int, float]` — per-rule baseline scores from
  `campaign.json`.
`weakest_rules` stays (first 6 of `all_rules`) for backward-compat. Reading
`status.json` uses the same tolerant `_read_json` (never raises; missing → None).
Elapsed time is NOT computed in the reader (keeps it clock-free/deterministic);
the app computes `now - started_at`.

### 4. App additions (`loop_tui`)

- **Current-iteration panel** (`#current`, top, below stats): pure helper
  `current_text(current, target_rule, elapsed_s, frame)` renders
  `#N/M · phase · elapsed · before-score · a judging→engine→verify→commit
  checklist`, with a spinner frame (`⠋⠙⠹…`) advanced each poll. Shows "idle
  between iterations" when `current` is None but the campaign is unfinished, and
  nothing once finished.
- **Expanded breakdown** — `breakdown_text` renders all measured rules (scrollable
  container) with a Δ-vs-baseline column (`+2.4`, `-` if unchanged/new) and marks
  the current target (the weakest rule) with `◀`.
- **Enriched diff** — the diff panel prepends the last iteration's commit subject
  (already available as `IterationRow.subject`) above the escaped diffstat.

All new render logic lives in pure module functions (tested without an event
loop); the App only wires them to widgets and advances the spinner frame.

## Implementation Decisions

- Harness change is confined to `ralph.sh` (`write_status` + calls). The template
  is copied at `loop init`, so existing worktrees need re-init to pick it up
  (documented; our self-run re-inits anyway).
- `status.json` is written with a temp-file + `mv` to avoid the reader seeing a
  half-written file; the reader's tolerance covers the rest.
- Backward compatibility: all campaign.json additions are new keys; older
  campaigns without `status.json`/baseline `commandments` render exactly as today
  (current panel shows "idle", Δ column shows `-`).
- Spinner state is the only per-frame mutable UI state; everything else is a pure
  function of the polled snapshot.

## Testing Decisions

- **Harness** (`test_loop_harness.py` extension): run with `engine=none` and assert
  `status.json` exists and reaches `phase: "done"`; assert `campaign.json`
  baseline has a `commandments` map.
- **Reader**: fixtures with a `status.json` → `current` populated; missing/`done`
  → `None`; `all_rules` returns all measured (not truncated); `baseline_rules`
  parsed; malformed `status.json` tolerated (no raise).
- **App render helpers**: `current_text` shows phase/elapsed/spinner and "idle"
  when None; `breakdown_text` shows Δ vs baseline + target marker over all rules.
- **Behaviour preservation**: existing dashboard/reader/CLI tests stay green; a
  campaign with no status.json/baseline-commandments still renders.

## Out of Scope

- Detecting the agent's *actual* chosen rule mid-iteration (only known at commit);
  the panel shows the weakest rule as the "likely target".
- Streaming claude's raw output into a structured view (the log pane already tails
  it).
- Pause/resume (still deferred).
