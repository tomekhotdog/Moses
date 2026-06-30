# Moses Loop TUI — Live Campaign Dashboard Design

## Research

The RALPH loop (`moses loop init|run|check|status`, driven by `loop_runner.py` +
`loop_template/ralph.sh`) is fully implemented and tested. Each iteration the
harness judges the target, hands `prompt.md` + `verdict.json` to a coding engine
(`claude`/`codex`), re-judges, reverts on regression, commits once, and appends an
audit record to `campaign.json`. It also writes a live `loop.log` and per-iteration
`verdict.json` / `after.json` into the state dir (`.moses/`).

Today the only ways to observe a running campaign are tailing `loop.log` or, after
the fact, `evals/analyse_campaign.py` and `evals/build_per_iter_presentation.py`.
There is no live, readable view of progress while the loop runs.

Existing rendering uses **Rich** (already a dependency; see `report/terminal.py`).
**Textual is not yet a dependency.** The campaign artifacts are all file-based and
written incrementally, so a viewer can stay fully decoupled from the loop by
polling those files.

## Problem Statement

Watching an autonomous Moses campaign is opaque: you cannot see the score
trajectory, which Commandment each iteration is attacking, whether iterations
improved or reverted, or the live log — all at once, as it happens. We want a
beautiful terminal dashboard that renders a campaign live, without changing what
the loop does.

## Solution

A new **`moses loop watch`** command launches a campaign and renders it live in a
**Textual** app; the existing **`moses loop run`** stays as the **headless** path.
Both drive the identical harness and read/write the identical artifacts — the TUI
is a *viewer* layered on top, so UI and headless runs can never diverge.

### Architecture (one-way data flow, three deep modules)

```
moses loop watch ──spawns──► ralph.sh (background Popen)
                                  │ writes (unchanged)
                                  ▼
                   campaign.json · loop.log · verdict.json/after.json
                                  │ polls every ~0.7s
                                  ▼
                   CampaignState (pure reader, no Textual)
                                  │ immutable snapshot
                                  ▼
                   MosesLoopApp (Textual widgets, render-only)
```

- **`loop_watch.py` — `CampaignState`**: a pure reader. Given a state dir, returns
  an immutable snapshot dataclass: baseline, best, iterations, log tail, the
  current verdict's weakest measured rules, and the last commit + diffstat. No
  Textual import; reads files only. **All testable logic lives here.**
- **`loop_tui.py` — `MosesLoopApp`**: the Textual app. Polls `CampaignState` on a
  timer, binds reactive widgets to the snapshot, renders. Never writes the ledger;
  it only supervises the subprocess and reads campaign state.
- **Launcher**: `watch` reuses `loop_run`'s env construction but spawns
  `bash ralph.sh` **non-blocking** (`subprocess.Popen`) instead of the blocking
  `subprocess.run`, supervises the process, and terminates it on quit.

### Panels

| Panel | Source | Shows |
|---|---|---|
| Header stats | campaign.json | baseline / best / iter N/max, grade |
| Score sparkline | campaign.json | score trajectory + total Δ |
| Iterations table | campaign.json | per-iter: Commandment targeted, before→after, Δviolations, ✓/revert |
| Commandment breakdown | verdict.json / after.json | weakest measured rules as bars; watch them climb |
| Diff / commit | git in worktree | last commit message + compact diffstat |
| Live log | loop.log | tail, scrollable |
| Summary screen | campaign.json | on completion: total gain, improved/reverted counts, best iteration, trajectory; offers to write the Markdown presentation |

### Behaviour decisions (locked)

- **Dependency**: `textual` is an **optional extra** (`moses[tui]`), keeping the
  core scorer lean. `watch` exits with a clear `uv pip install moses[tui]` message
  if Textual is absent.
- **Pause**: **out of v1**. Clean mid-campaign pause needs `ralph.sh` to poll a
  pause-file between iterations (a harness change); deferred. Footer keybindings:
  `[q]uit` (terminates the subprocess), `[↑↓]` scroll log.
- **Auto-init**: `moses loop watch <target>` **inits a campaign if none exists**
  (worktree mode by default), for true one-command UX; attaches to an existing
  campaign otherwise.

## User Stories

1. As an operator, I run `moses loop watch .` and immediately see a live dashboard
   of the campaign — score trajectory, per-iteration outcomes, and the log — so I
   can tell at a glance whether the loop is making honest progress.
2. As an operator, I watch the Commandment breakdown bars climb as iterations land,
   so I can see *which* design qualities are improving.
3. As a scripter, I run `moses loop run` headless (no TUI, no new dependency) and
   get the identical campaign behaviour and `campaign.json`.
4. On completion, I get a summary screen and can write the Markdown presentation
   without leaving the tool.

## Implementation Decisions

- New modules `src/moses/loop_watch.py` (`CampaignState` + snapshot dataclasses)
  and `src/moses/loop_tui.py` (`MosesLoopApp` + widgets). New CLI subcommand
  `loop watch` in `cli.py` mirroring `run`'s options (`--worktree`,
  `--max-iterations`, `--engine`, `--cooldown`, `--max-hours`, plus `--target` /
  `--target-path` for auto-init).
- `pyproject.toml`: add optional extra `tui = ["textual>=0.80"]` (confirm/pin the
  exact installed minor via `uv add` at implementation time). `loop watch` imports
  Textual lazily and prints the install hint on `ImportError`.
- Reuse, don't duplicate: the sparkline reuses
  `evals/build_per_iter_presentation.py:sparkline` logic (lift the shared helper
  into the package so both the TUI and the offline presentation import one copy);
  the summary reuses `analyse_campaign.py`'s aggregation. Lifting these into
  `loop_watch.py` keeps a single source of truth.
- Non-blocking launch: factor `loop_run`'s env-building into a helper
  (`_loop_env`) reused by both the blocking `loop_run` and the `watch` launcher,
  so the two stay in lockstep.
- **Deep modules**: `CampaignState` hides all file parsing behind a small "give me
  the current snapshot" interface; `MosesLoopApp` hides all widget/layout detail
  behind "render this snapshot". Each is understandable and testable in isolation.

## Testing Decisions

- **`CampaignState` reader (primary coverage)**: unit tests over fixture state dirs
  (hand-written `campaign.json` + `loop.log` + `verdict.json`): parses iterations,
  computes per-iteration and total deltas, tails the log, extracts the weakest
  measured Commandments, derives the diffstat, and — critically — tolerates
  partial/missing/mid-append files by returning last-good or empty fields without
  raising.
- **`MosesLoopApp` (smoke)**: Textual's `run_test`/pilot harness — mount the app
  against a fixture state dir, assert each panel renders expected text, and assert
  that a completed campaign transitions to the summary screen.
- **Launcher**: assert `watch` builds the correct subprocess env (shared with
  `loop_run`) and that quitting terminates the supervised subprocess (mock
  `Popen`).
- **Behaviour preservation**: the existing loop tests stay green; `moses loop run`
  is unchanged. No commandment, weight, or scoring code is touched.

## Out of Scope

- **Pause/resume** mid-campaign (needs a `ralph.sh` cooperation point) — deferred.
- **Attaching to a campaign on a remote machine** — local state dir only.
- **Editing campaign state from the UI** — the TUI is strictly read-only over the
  ledger; it only supervises the subprocess.
- **Replacing the offline reporters** — `analyse_campaign.py` /
  `build_per_iter_presentation.py` remain for headless/CI use; the TUI shares their
  logic but does not delete them.
