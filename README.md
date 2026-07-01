# Moses — Code Quality Oracle

![Moses](Moses.png)

**Judge your Python codebase against 31 design Commandments. Score 0–100, get a Grade A–F, and run autonomous improvements via the RALPH loop — watched live in a terminal dashboard.**

## What is Moses?

A static code quality oracle that reads a Python source tree and judges it against design principles distilled from Ousterhout (*A Philosophy of Software Design*), Martin (*Clean Code*), McConnell (*Code Complete*), and the Gang of Four. It produces:

- **Score** (0–100) and **Grade** (A–F)
- Per-Commandment metrics and violations
- Ranked **Hotspots** (files dragging the Score down)
- Machine-readable **JSON** and styled **HTML** reports
- An impartial baseline for improvement campaigns

The scorer is **pure Python + radon** — deterministic, no LLM, no network. An LLM only appears in the optional autonomous *loop*, where it serves as the developer making improvements. Moses stays the judge.

## Quick Start

```bash
pip install -e .
moses judge src/
```

Or with `uv`:

```bash
uv sync
uv run moses judge src/
```

## CLI

```
moses judge <path> [--json out.json] [--html out.html] [--deep]
moses prompt <N>                    # curated brief for Commandment N
moses loop init <repo> [--in-place] # start an improvement campaign
moses loop run --worktree <wt>      # run autonomous improvements (headless)
moses loop watch <repo> [--in-place] [--max-iterations N]  # launch + live TUI dashboard
moses loop check --worktree <wt>    # validate campaign audit trail
moses loop status --worktree <wt>   # progress summary
```

The dashboard needs the optional `tui` extra: `uv sync --extra tui` (or `pip install 'moses[tui]'`).

Exit codes: `0` for grades A/B/C, `1` for D/E, `2` for F.

## The 31 Commandments

| # | Status |
|----|--------|
| 1–6, 11–18, 20–25, 27, 29, 30, 31 | ✅ Implemented (24 rules; 23 in the MVP scoring set, C4 implemented but held out) |
| 7–10, 19, 26, 28 | 📋 Planned |

See [`docs/commandments.md`](docs/commandments.md) for details. Per-rule briefs in [`docs/commandments/NN-*.md`](docs/commandments/).

## The Autonomous Loop (RALPH)

Run an improvement campaign:

```bash
moses loop init my-repo
moses loop run --worktree my-repo/.moses-loop
```

The harness:
1. **Judges** the codebase and records a baseline Verdict
2. **Hands off** to a coding engine (Claude, Codex, or none) with `prompt.md` + `verdict.json`
3. **Verifies** the change improved the Score and didn't raise violations
4. **Commits** the improvement
5. **Records** an audit trail in `campaign.json`

Honest, monotonic improvement only — regressions are reverted, never recorded.

### Live dashboard

`moses loop watch` launches a campaign and renders it live (Textual). `moses loop
run` remains the headless path; the dashboard is a read-only view over the same
`campaign.json`/`loop.log`, so the two never diverge.

```
┌ Moses Loop ─────────────────────────────── 08:41 ┐
│ baseline 82.3 A     best 84.9 A     iter 4/10     │
│ Score ▁▃▄▆▇   82.3 → 84.9  (+2.6)                 │
├────────────────────────────┬─────────────────────┤
│ #  Cmd  Before After ΔViol  │ Weakest commandments │
│ 1  C25  82.3   83.1   -6  ✓ │ C16 ██········  0.0   │
│ 2  C16  83.1   83.1    0  ⟲ │ C25 ████······ 22.4  │
│ 3  C18  83.1   84.0   -3  ✓ │ C18 ██████···· 55.0  │
│ 4  C14  84.0 … running ⠋     │ C14 ███████··· 72.5  │
│                             │ C21 ████████·· 80.1  │
│ Last change                 │ C27 █████████· 90.0  │
│ c14 flatten guard clauses   │                      │
│  engine.py | 8 +---         │                      │
├─────────────────────────────┴─────────────────────┤
│ 08:41:02 before: score=84.0 violations=61          │
│ 08:41:19 improved: 84.0 -> 84.9, viol 61 -> 58     │
│ 08:41:20 committed @ 9a3f1c2                        │
├────────────────────────────────────────────────────┤
│  q Quit    ↑↓ Scroll log                            │
└────────────────────────────────────────────────────┘
```

Keys: `q` quit (terminates the harness), `↑/↓` scroll the log. On completion a
summary screen shows total gain, improved/reverted counts, and the trajectory.

## Architecture

```
src/moses/
  ├── engine.py              # core scorer: iterates 31 Commandments
  ├── commandments/          # rule implementations (21 of 31)
  ├── loader.py              # load codebase, ignore vendored/test dirs
  ├── config.py              # weights, enabled-set, deep mode
  ├── cli.py                 # judge/prompt/loop commands
  ├── loop_runner.py         # loop_init/run/spawn/check/status
  ├── loop_watch.py          # pure CampaignState reader for the dashboard
  ├── loop_tui.py            # Textual live dashboard (moses loop watch)
  ├── models.py              # SourceFile, Codebase, Verdict, etc.
  ├── report/                # terminal + HTML rendering
  ├── loop_template/         # prompt.md, ralph.sh, check_invariants.py
  └── data/                  # commandment_prompts.yaml
tests/
  ├── unit/                  # rule, engine, config, reader + TUI tests
  └── integration/           # CLI, loop, harness, watch, spawn tests
docs/
  ├── spec.md                # architecture & design
  ├── commandments.md        # rule reference
  ├── language.md            # canonical terminology
  ├── lessons.md             # build lessons & gotchas
  └── commandments/          # 31 per-rule briefs
evals/
  ├── analyse_campaign.py    # summarise loop progress
  └── build_per_iter_presentation.py  # render iteration report
```

## Scoring

```
Score = Σ (wᵢ · Sᵢ) / Σ wᵢ    for enabled, measured rules only
```

**Key invariant:** Disabling a rule never pads the Score with a free 100. Both numerator and denominator exclude disabled/unmeasured rules.

| Grade | Score |
|-------|-------|
| A | ≥ 80 |
| B | ≥ 65 |
| C | ≥ 50 |
| D | ≥ 35 |
| E | ≥ 20 |
| F | < 20 |

## Self-Hosted

Moses judges itself:

```bash
moses judge src/moses
# Score 83.2/100  Grade A
```

## Tests

```bash
uv run pytest
# 193 passed, 1 skipped
```

Unit tests cover cheap rules, heavier structural rules, engine, config, models, and the dashboard reader/render helpers. Integration tests cover CLI (judge, prompt, JSON/HTML output) and the loop (init, run, spawn, watch, harness, status, check, invariant validation).

## Design Principles

1. **Pure scorer:** stdlib + radon only; deterministic; no network calls
2. **Per-rule isolation:** each rule wrapped in try/except; failures become `status="error"` and never abort the run
3. **Honest audit trail:** the loop records only unprompted, monotonic improvements
4. **Opt-in complexity:** mutation testing (#20) requires `--deep`; disabled rules never inflate the Score
5. **Reproducible:** same source → same Score, same Verdict JSON

## Docs & Resources

- [`docs/spec.md`](docs/spec.md) — full specification
- [`docs/commandments.md`](docs/commandments.md) — all 31 rules at a glance
- [`docs/language.md`](docs/language.md) — canonical terminology
- [`docs/lessons.md`](docs/lessons.md) — build lessons, gotchas, design decisions
- [`docs/commandments/NN-*.md`](docs/commandments/) — per-Commandment briefs (31 files)

## Author

Built as a code quality oracle inspired by Ousterhout, Martin, McConnell, and the GoF. Implemented with Python, AST analysis, and radon.

---

**Status:** MVP complete. 24 of 31 rules implemented (23 in the scoring set). Self-hosted at Grade A (83.2). Autonomous campaigns with a live terminal dashboard.
