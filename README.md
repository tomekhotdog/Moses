# Moses — Code Quality Oracle

![Moses](Moses.png)

**Judge your Python codebase against 31 design Commandments. Score 0–100, get a Grade A–F, and run autonomous improvements via the RALPH loop.**

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
moses loop run --worktree <wt>      # run autonomous improvements
moses loop check --worktree <wt>    # validate campaign audit trail
moses loop status --worktree <wt>   # progress summary
```

Exit codes: `0` for grades A/B/C, `1` for D/E, `2` for F.

## The 31 Commandments

| # | Name | Weight | Status |
|----|------|--------|--------|
| 1–6, 11–18, 20–25, 29, 31 | _Implemented (21 rules)_ | _67/100_ | ✅ |
| 4, 7–10, 19, 26–28, 30 | _Planned_ | _33/100_ | 📋 |

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

## Architecture

```
src/moses/
  ├── engine.py              # core scorer: iterates 31 Commandments
  ├── commandments/          # rule implementations (21 of 31)
  ├── loader.py              # load codebase, ignore vendored/test dirs
  ├── config.py              # weights, enabled-set, deep mode
  ├── cli.py                 # judge/prompt/loop commands
  ├── loop_runner.py         # loop_init/run/check/status
  ├── models.py              # SourceFile, Codebase, Verdict, etc.
  ├── report/                # terminal + HTML rendering
  ├── loop_template/         # prompt.md, ralph.sh, check_invariants.py
  └── data/                  # commandment_prompts.yaml
tests/
  ├── unit/                  # 60 unit tests
  └── integration/           # 11 CLI + loop smoke tests
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
moses judge . --exclude 'tests/fixtures/*'
# Score 79.6/100  Grade B
```

## Tests

```bash
uv run pytest
# 71 passed, 1 skipped
```

Unit tests cover cheap rules, heavier structural rules, engine, config, and models. Integration tests cover CLI (judge, prompt, JSON/HTML output) and loop (init, status, check, invariant validation).

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

**Status:** MVP complete. 21 of 31 rules implemented. Self-hosted at Grade B. Ready for improvement campaigns.
