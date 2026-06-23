# AoC Calibration Corpus (Phase 1 — Pilot) Design

## Research

### Moses infrastructure that the corpus reuses

- **Programmatic scoring:** `engine.run(root, config: Config | None = None) -> Verdict`
  (`engine.py:98`). `load_codebase` (`loader.py`) accepts a **single `.py` file**
  or a directory, so each solution file can be scored independently.
- **Verdict** (`models.py:86`): `score`, `grade`, `commandments:
  list[CommandmentResult]`, `hotspots`, `overview`, `meta`; `to_dict()` for JSON.
  Per-rule `CommandmentResult` exposes `number`, `score_contribution`, `metric`,
  `status`, `violations`.
- **Config** (`config.py`): `Config(enabled=..., excludes=..., deep=...)`. Default
  is `MVP_COMMANDMENTS` (now includes 27).
- **`evals/` conventions:** standalone scripts (`analyse_campaign.py`,
  `build_per_iter_presentation.py`) with `main(argv)` + `argparse` +
  `raise SystemExit(main())`, run via `uv run python evals/x.py`. JSON for data
  interchange; one builds a Markdown report (sparklines, tables) — reusable
  patterns for the comparison file.
- **Report infra:** `report/html.py` (`render_html`, grade colors, table/bar
  builders) and `report/terminal.py` (Rich tables) — borrowable if HTML output is
  later wanted.
- **Constraint (load-bearing):** rules' `evaluate(codebase)` do **not** receive
  `Config`; tunables are module constants (e.g. C27 `TARGET_RATIO = 0.6`). So
  Phase-2 parameter calibration needs a config-threading mechanism that does not
  exist yet (deferred during C27, recorded in `lessons.md`).

### The AoC source repo

`github.com/tomekhotdog/AdventOfCode` — years 2020–2025 present; 2024 complete in
Python. Layout: `2024/qN.py` (one solution file per day 1–25) + `2024/inputs/`.
2022 and 2023 are full (held-out test set).

Filtering the user's own 2024 solutions to ≥50 non-blank lines yields **15
training candidates**: q4 (78), q6 (154), q8 (95), q9 (104), q10 (89), q12 (124),
q13 (55), q14 (82), q15 (166), q16 (126), q17 (118), q20 (83), q21 (127), q22
(53), q24 (144). The other 10 (21–48 lines) are filtered as noise.

## Problem Statement

Moses' rule parameters (weights, curves, thresholds like C27's `TARGET_RATIO`)
are hand-set and uncalibrated. We need a labelled corpus of varied-quality
solutions to the *same* problems so we can compare Moses' deterministic score
against a holistic "Truth" proxy (an LLM-as-judge), see where they diverge, and
later tune parameters until they track. Advent-of-Code gives small/medium,
well-scoped problems with many public solutions and real room for domain modelling.

## Solution

**Phase 1 (this design): a 3-question pilot** (q4, q9, q16 — easy/medium/hard mix)
that assembles ~5 solutions each, scores every solution two ways *independently*,
and produces one comparison file exposing Moses-vs-judge agreement. Scaling to all
15 and the 2022/23 test set, and the Phase-2 calibration loop, follow once the
pilot validates the format and the judge.

### Solution sourcing (per user)

Try **real online mining first** (Reddit AoC megathreads / GitHub, best-effort),
and **synthesize to fill** any question left under-covered. Synthesized solutions
deliberately span a bad→excellent quality spectrum, which doubles as the judge
validation (a correct judge must rank known-better solutions higher).

### Directory layout (under `evals/`)

```
evals/corpus/
  2024/q4/  q9/  q16/
    problem.md            # 2–3 line problem statement (judge context)
    tomek.py              # the user's real solution (copied from AoC repo)
    online_1.py …         # mined real solutions, where found
    synth_<tier>.py …     # synthesized fills (e.g. synth_primitive, synth_clean)
    judgements.json       # LLM-judge output per solution
  comparison.json         # merged data backbone (reproducible)
  comparison.md           # the single human-readable comparison file
```

### Data flow — agent judgment vs deterministic scoring (kept separate)

1. **Agent (me/subagents):** gather solution files; **judge** each — a subagent
   sees only the solution code + `problem.md`, never Moses output (independence
   prevents anchoring) — returns structured `{pct: 0–100, justification, notes}`
   → `judgements.json` per question.
2. **`evals/corpus_score.py` (deterministic):** `engine.run(file, Config())` per
   solution → Moses score/grade/per-commandment → contributes to `comparison.json`.
3. **`evals/corpus_report.py` (deterministic):** merges judgements + Moses scores
   → `comparison.md`: per-question tables (solution · LOC · Moses score · grade ·
   judge % · short justification · notable commandment hits) **plus a correlation
   summary** (per-question rank agreement Moses-vs-judge, and a Moses−judge gap
   column). Merge + correlation + formatting hide behind one
   `build_comparison(corpus_dir) -> str` (deep module).

### LLM-judge rubric (the Truth proxy)

A single holistic code-quality % + justification, judging: readability & naming,
domain modelling/abstraction, simplicity vs over-engineering, structure/
decomposition, error handling. Deliberately **not** Moses' mechanical formula, so
the two are independent signals. Consistency comes from one fixed rubric prompt
reused for every solution.

## User Stories

1. As the Moses author, I want each pilot solution scored by both Moses and an
   independent LLM-judge in one file, so I can see where the deterministic oracle
   diverges from holistic judgment.
2. As the author, I want a known bad→excellent synthesized spectrum per question,
   so I can confirm the judge ranks quality correctly (validating it as a Truth
   proxy).
3. As the author, I want the corpus reproducible (data in JSON, scoring in a
   script) so re-running after adding solutions is one command.
4. As the author, I want to intervene with my own opinions on any solution and
   have that captured, so the corpus reflects ground truth I trust.

## Implementation Decisions

- **Two deterministic scripts** (`corpus_score.py`, `corpus_report.py`) following
  the `evals/` `main(argv)` convention; the agentic steps (gather, judge) write
  JSON the scripts consume. This keeps scoring/reporting reproducible and
  re-runnable independently of the (non-deterministic) judging.
- **Judge via dispatched subagents**, one per solution, fixed rubric prompt, no
  access to Moses results — parallelizable and independent.
- **Markdown comparison file** first (diffable, fits `evals/`); HTML deferred
  unless wanted. JSON backbone enables re-rendering without re-judging/re-scoring.
- **Single-file Moses scoring is accepted** even though some rules (DRY, deep
  modules) behave differently on one file — that behaviour is itself part of what
  calibration will surface.
- **Deep module:** `build_comparison(corpus_dir)` — callers get a report string;
  correlation math and table formatting stay inside.

## Testing Decisions

- Unit-test `corpus_report.py`'s pure pieces: the correlation/rank-agreement
  function (fixed inputs → known Spearman/gap) and a small `build_comparison` over
  a tiny synthetic corpus dir → asserts the table contains expected rows. These
  are deterministic and worth pinning.
- `corpus_score.py` is thin glue over `engine.run` (already well-tested); a single
  smoke test that it scores a fixture solution and writes the expected JSON shape.
- The judgements themselves are not unit-tested (they're agent output); their
  sanity check is the synthesized-spectrum ranking, reviewed by the user.
- Reuse `uv run pytest`; put tests under `tests/unit/` alongside the rest.

## Out of Scope

- **All 15 training questions** and the **2022/23 test set** — scale after the
  pilot is validated.
- **Phase-2 calibration loop** and the **config-threading / parameter-override
  mechanism** it needs — separate design+build.
- **Any change to Moses rules or weights** — the corpus only observes; it does not
  tune yet.
- **HTML comparison output** — Markdown only for the pilot.
