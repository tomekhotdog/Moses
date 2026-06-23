# AoC Calibration Corpus (Phase 1 Pilot) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use tomek-superpowers:build to implement this plan task-by-task.

**Goal:** For pilot questions q4/q9/q16, assemble ~5 solutions each, score every solution with both Moses and an independent LLM-judge, and produce one `comparison.md` exposing where they diverge.
**Architecture:** Two deterministic `evals/` scripts (`corpus_score.py` runs Moses → `moses_scores.json`; `corpus_report.py` merges Moses + judge → `comparison.json` + `comparison.md`) consume JSON produced by agentic steps (gather solutions, judge them). Clean split: judging is agentic and Moses-blind; scoring/reporting are reproducible scripts.
**Tech Stack:** Python stdlib, `moses.engine.run`, pytest. No new deps (Spearman implemented by hand).
**Design:** `docs/plans/2026-06-23-aoc-calibration-corpus-design.md`

Work directly on `main` (user preference — no feature branch). Run tests with `uv run pytest` (sandbox disabled; per `docs/lessons.md`). The user's AoC repo is cloned at `/private/tmp/claude-501/-Users-tomaszszymaniec-Documents-Projects-Moses/2d5713d7-331d-45a6-a99d-b175af0a9df9/scratchpad/aoc` (solutions at `aoc/2024/qN.py`).

## Data schemas (authoritative)

`evals/corpus/moses_scores.json` (written by Task 1):
```json
{"year": "2024",
 "questions": {
   "q4": {
     "tomek.py": {"loc": 78, "moses_score": 64.2, "grade": "C",
                  "commandments": {"1": 100.0, "12": 88.0, "27": 54.4}},
     "synth_primitive.py": {"loc": 40, "moses_score": 41.0, "grade": "D", "commandments": {}}
   }}}
```

`evals/corpus/2024/qN/judgements.json` (written by Task 4, keyed by solution filename):
```json
{"tomek.py": {"pct": 72, "justification": "Clear decomposition; some primitive lists."},
 "synth_primitive.py": {"pct": 35, "justification": "One long function, stringly-typed."}}
```

---

### Task 1: `corpus_score.py` — deterministic Moses scoring — ✅ COMPLETE (68c1e39)
**Depends on:** none

**Files:**
- Create: `evals/__init__.py` (empty — makes `evals` importable in tests)
- Create: `evals/corpus_score.py`
- Modify: `pyproject.toml` (add `"."` to pytest `pythonpath`)
- Test: `tests/unit/test_corpus_score.py`

**Step 1: Write the failing test**
```python
"""corpus_score: run Moses over a corpus tree and emit moses_scores.json."""

from __future__ import annotations

import json
from pathlib import Path

from evals.corpus_score import score_corpus


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def test_score_corpus_shape(tmp_path):
    root = tmp_path / "corpus"
    _write(root / "2024" / "q1" / "a.py", "def add(x: int, y: int) -> int:\n    return x + y\n")
    _write(root / "2024" / "q1" / "b.py", "x = 1\nclass C:\n    def m(self):\n        return x\n")
    result = score_corpus(root, "2024")
    assert result["year"] == "2024"
    q1 = result["questions"]["q1"]
    assert set(q1) == {"a.py", "b.py"}
    for entry in q1.values():
        assert isinstance(entry["moses_score"], float)
        assert entry["grade"] in {"A", "B", "C", "D", "E", "F"}
        assert isinstance(entry["loc"], int) and entry["loc"] > 0
        assert isinstance(entry["commandments"], dict)


def test_score_corpus_writes_json(tmp_path):
    root = tmp_path / "corpus"
    _write(root / "2024" / "q1" / "a.py", "def add(x: int, y: int) -> int:\n    return x + y\n")
    from evals.corpus_score import main

    rc = main(["--corpus", str(root), "--year", "2024"])
    assert rc == 0
    data = json.loads((root / "moses_scores.json").read_text())
    assert "q1" in data["questions"]
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_corpus_score.py -q`
Expected: FAIL (ModuleNotFoundError: evals.corpus_score)

**Step 3: Write minimal implementation**
First add `"."` to the pytest pythonpath. In `pyproject.toml`, under `[tool.pytest.ini_options]`, change `pythonpath = ["src"]` to `pythonpath = ["src", "."]` (read the file first; match exact formatting).

Create `evals/__init__.py` empty.

Create `evals/corpus_score.py`:
```python
"""Score every solution in a corpus tree with Moses -> moses_scores.json.

Deterministic half of the calibration corpus: walks ``<corpus>/<year>/<qN>/*.py``,
runs ``moses.engine.run`` on each solution file, and records Score/grade/per-rule
contributions. The LLM-judge half is produced separately (see corpus_report.py).

Usage: uv run python evals/corpus_score.py --corpus evals/corpus --year 2024
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from moses.config import Config
from moses.engine import run


def score_corpus(corpus_root: Path, year: str) -> dict:
    """Score all solutions under ``corpus_root/year`` and return the data dict."""
    corpus_root = Path(corpus_root)
    out: dict = {"year": year, "questions": {}}
    year_dir = corpus_root / year
    for qdir in sorted(p for p in year_dir.iterdir() if p.is_dir()):
        solutions: dict = {}
        for sol in sorted(qdir.glob("*.py")):
            verdict = run(sol, Config())
            commandments = {
                str(c.number): c.score_contribution
                for c in verdict.commandments
                if c.status == "measured"
            }
            solutions[sol.name] = {
                "loc": verdict.overview["non_blank_loc"],
                "moses_score": round(verdict.score, 2),
                "grade": verdict.grade,
                "commandments": commandments,
            }
        out["questions"][qdir.name] = solutions
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="evals/corpus", help="Corpus root directory")
    parser.add_argument("--year", default="2024", help="Year subdirectory to score")
    args = parser.parse_args(argv)

    corpus_root = Path(args.corpus)
    data = score_corpus(corpus_root, args.year)
    out_path = corpus_root / "moses_scores.json"
    out_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(data['questions'])} questions)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_corpus_score.py -q`
Expected: PASS

**Step 5: Commit**
```bash
git add evals/__init__.py evals/corpus_score.py pyproject.toml tests/unit/test_corpus_score.py
git commit -m "feat(corpus): deterministic Moses scoring of solution trees"
```

---

### Task 2: `corpus_report.py` — merge + correlation + comparison.md — ✅ COMPLETE (c939cca)
**Depends on:** Task 1 (consumes the `moses_scores.json` schema)

**Files:**
- Create: `evals/corpus_report.py`
- Test: `tests/unit/test_corpus_report.py`

**Step 1: Write the failing test**
```python
"""corpus_report: rank-agreement math and the merged comparison markdown."""

from __future__ import annotations

import json
from pathlib import Path

from evals.corpus_report import build_comparison, rank_agreement


def test_rank_agreement_perfect():
    pairs = [(10.0, 1.0), (20.0, 2.0), (30.0, 3.0)]
    assert rank_agreement(pairs)["spearman"] == 1.0


def test_rank_agreement_inverted():
    pairs = [(10.0, 3.0), (20.0, 2.0), (30.0, 1.0)]
    assert rank_agreement(pairs)["spearman"] == -1.0


def test_rank_agreement_too_few():
    assert rank_agreement([(10.0, 1.0)])["spearman"] is None


def _corpus(tmp_path: Path) -> Path:
    root = tmp_path / "corpus"
    (root / "2024" / "q1").mkdir(parents=True)
    moses = {
        "year": "2024",
        "questions": {
            "q1": {
                "good.py": {"loc": 50, "moses_score": 85.0, "grade": "A", "commandments": {"27": 90.0}},
                "bad.py": {"loc": 40, "moses_score": 40.0, "grade": "D", "commandments": {"27": 10.0, "16": 0.0}},
            }
        },
    }
    (root / "moses_scores.json").write_text(json.dumps(moses), encoding="utf-8")
    judge = {
        "good.py": {"pct": 88, "justification": "Clean, well modelled."},
        "bad.py": {"pct": 30, "justification": "Stringly typed, duplicated."},
    }
    (root / "2024" / "q1" / "judgements.json").write_text(json.dumps(judge), encoding="utf-8")
    return root


def test_build_comparison_contains_rows_and_correlation(tmp_path):
    root = _corpus(tmp_path)
    md = build_comparison(root, "2024")
    assert "q1" in md
    assert "good.py" in md and "bad.py" in md
    assert "85.0" in md  # moses score present
    assert "88" in md     # judge pct present
    # good and bad agree in rank between moses and judge -> spearman 1.0
    assert "1.0" in md
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_corpus_report.py -q`
Expected: FAIL (ModuleNotFoundError: evals.corpus_report)

**Step 3: Write minimal implementation**
Create `evals/corpus_report.py`:
```python
"""Merge Moses scores with LLM-judge scores into a comparison report.

Reads ``<corpus>/moses_scores.json`` (from corpus_score.py) and each
``<corpus>/<year>/<qN>/judgements.json`` (agentic LLM-judge output), and writes a
single ``comparison.md`` (plus merged ``comparison.json``) laying the deterministic
Moses Score beside the holistic Judge score, with a per-question rank-agreement
summary.

Usage: uv run python evals/corpus_report.py --corpus evals/corpus --year 2024
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _ranks(xs: list[float]) -> list[float]:
    """Average (tie-corrected) 1-based ranks."""
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def _pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    if n == 0:
        return 0.0
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    va = sum((x - ma) ** 2 for x in a)
    vb = sum((x - mb) ** 2 for x in b)
    denom = (va * vb) ** 0.5
    return cov / denom if denom else 0.0


def rank_agreement(pairs: list[tuple[float, float]]) -> dict:
    """Spearman rho between the Moses and Judge scores in ``pairs``."""
    if len(pairs) < 2:
        return {"spearman": None, "n": len(pairs)}
    moses = [p[0] for p in pairs]
    judge = [p[1] for p in pairs]
    rho = _pearson(_ranks(moses), _ranks(judge))
    return {"spearman": round(rho, 3), "n": len(pairs)}


def merge(corpus_root: Path, year: str) -> dict:
    """Merge Moses + judge data into one structure keyed by question/solution."""
    corpus_root = Path(corpus_root)
    moses = json.loads((corpus_root / "moses_scores.json").read_text(encoding="utf-8"))
    merged: dict = {"year": year, "questions": {}}
    for qname, sols in moses["questions"].items():
        jpath = corpus_root / year / qname / "judgements.json"
        judge = json.loads(jpath.read_text(encoding="utf-8")) if jpath.exists() else {}
        rows = {}
        for fname, m in sols.items():
            j = judge.get(fname, {})
            rows[fname] = {
                "loc": m["loc"],
                "moses_score": m["moses_score"],
                "grade": m["grade"],
                "commandments": m["commandments"],
                "judge_pct": j.get("pct"),
                "judge_justification": j.get("justification", ""),
            }
        merged["questions"][qname] = rows
    return merged


def _weakest(commandments: dict, k: int = 3) -> str:
    """The k lowest-scoring measured commandments, as 'N:score' tags."""
    items = sorted(commandments.items(), key=lambda kv: kv[1])[:k]
    return ", ".join(f"#{n}:{int(round(s))}" for n, s in items) if items else "—"


def build_comparison(corpus_root: Path, year: str) -> str:
    """Render the merged corpus as a Markdown comparison report."""
    data = merge(corpus_root, year)
    lines = [f"# Calibration corpus — Moses vs Judge ({year})", ""]
    summary: list[str] = []
    for qname, rows in data["questions"].items():
        lines.append(f"## {qname}")
        lines.append("")
        lines.append("| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |")
        lines.append("|---|---|---|---|---|---|---|---|")
        pairs: list[tuple[float, float]] = []
        for fname, r in sorted(rows.items(), key=lambda kv: (kv[1]["judge_pct"] is None, -(kv[1]["judge_pct"] or 0))):
            judge = r["judge_pct"]
            gap = "" if judge is None else f"{r['moses_score'] - judge:+.1f}"
            if judge is not None:
                pairs.append((r["moses_score"], float(judge)))
            just = r["judge_justification"].replace("|", "\\|")
            judge_s = "—" if judge is None else str(judge)
            lines.append(
                f"| {fname} | {r['loc']} | {r['moses_score']} | {r['grade']} | "
                f"{judge_s} | {gap} | {_weakest(r['commandments'])} | {just} |"
            )
        agree = rank_agreement(pairs)
        rho = agree["spearman"]
        rho_s = "n/a" if rho is None else str(rho)
        lines.append("")
        lines.append(f"Rank agreement (Spearman ρ, Moses vs Judge): **{rho_s}** (n={agree['n']})")
        lines.append("")
        summary.append(f"| {qname} | {rho_s} | {agree['n']} |")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Question | Spearman ρ | n |")
    lines.append("|---|---|---|")
    lines.extend(summary)
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--corpus", default="evals/corpus")
    parser.add_argument("--year", default="2024")
    args = parser.parse_args(argv)

    corpus_root = Path(args.corpus)
    merged = merge(corpus_root, args.year)
    (corpus_root / "comparison.json").write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    md = build_comparison(corpus_root, args.year)
    (corpus_root / "comparison.md").write_text(md, encoding="utf-8")
    print(f"Wrote {corpus_root / 'comparison.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

**Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_corpus_report.py -q`
Expected: PASS

**Step 5: Commit**
```bash
git add evals/corpus_report.py tests/unit/test_corpus_report.py
git commit -m "feat(corpus): merge Moses+Judge into comparison.md with rank agreement"
```

---

### Task 3: Gather pilot solutions (agentic — data, no unit tests) — ✅ COMPLETE (28ddc24)
**Depends on:** none (independent of Tasks 1–2; needed before Task 4)

For each pilot question **q4, q9, q16** create `evals/corpus/2024/qN/` containing:
- `problem.md` — a 2–3 line statement of the AoC 2024 puzzle (q4 = "Ceres Search", word-search for XMAS; q9 = "Disk Fragmenter", compact a disk map; q16 = "Reindeer Maze", lowest-cost path with turn penalties). Keep factual and brief.
- `tomek.py` — copy verbatim from the cloned repo `…/scratchpad/aoc/2024/qN.py`.
- **Mine online first (best-effort):** web-search GitHub/Reddit for real 2024 day-N Python solutions; save 1–3 that PARSE (`python -c "import ast,sys; ast.parse(open(sys.argv[1]).read())"`) as `online_1.py`, `online_2.py`, …. If mining yields nothing usable for a question, note it.
- **Synthesize to fill** so each question has **≥5 total** solutions AND spans a deliberate quality spectrum: at minimum a `synth_primitive.py` (deliberately poor — one giant function, stringly-typed, magic numbers) and a `synth_clean.py` (excellent — domain-modelled, decomposed, typed). These must actually solve the same problem (use the example input in `…/aoc/2024/inputs/qN_example*.txt` to sanity-check logic where practical).

**Verification (no unit test — this is data):**
- `ls evals/corpus/2024/q4 evals/corpus/2024/q9 evals/corpus/2024/q16` shows ≥5 `.py` each + `problem.md`.
- Every `.py` parses: `for f in evals/corpus/2024/*/*.py; do uv run python -c "import ast,sys;ast.parse(open(sys.argv[1]).read())" "$f" || echo "PARSE FAIL $f"; done` prints no failures.

**Commit:**
```bash
git add evals/corpus/2024
git commit -m "data(corpus): gather pilot solutions for q4/q9/q16"
```

---

### Task 4: Judge each solution (agentic — Moses-blind) — ✅ COMPLETE (b0a… judgements commit)
**Depends on:** Task 3

For each pilot question, dispatch a judge subagent that is given ONLY the question's `problem.md` and its solution `.py` files (NEVER any Moses score). It applies this fixed rubric and returns one holistic code-quality % (0–100) + a one-sentence justification per solution:

> Rubric — judge overall code quality as a senior engineer: readability & naming, domain modelling / abstraction, simplicity vs over-engineering, structure & decomposition, error handling. One integer percentage per solution with a one-sentence justification. Score absolutely (not just relative), but ensure a clearly-better solution scores higher than a clearly-worse one.

Write each question's results to `evals/corpus/2024/qN/judgements.json` keyed by filename (schema above).

**Verification (no unit test):**
- Each `judgements.json` is valid JSON with a `{pct, justification}` entry for every `.py` in its dir: 
  `uv run python -c "import json,glob,os,sys;[ ( (lambda d,q: [print('MISSING',q,s) for s in [os.path.basename(p) for p in glob.glob(q+'/*.py')] if s not in d])(json.load(open(q+'/judgements.json')), q) ) for q in glob.glob('evals/corpus/2024/q*')]"` prints nothing.
- Sanity: in each question, `synth_clean.py` pct > `synth_primitive.py` pct (judge ranks the known spectrum correctly). If not, STOP and report — the judge or rubric needs revisiting before trusting it.

**Commit:**
```bash
git add evals/corpus/2024/*/judgements.json
git commit -m "data(corpus): LLM-judge scores for pilot solutions"
```

---

### Task 5: Run the pipeline end-to-end + review (integration) — ✅ COMPLETE
**Depends on:** Tasks 1, 2, 3, 4

**Steps:**
1. `uv run python evals/corpus_score.py --corpus evals/corpus --year 2024` → writes `evals/corpus/moses_scores.json`. Confirm it scored q4/q9/q16.
2. `uv run python evals/corpus_report.py --corpus evals/corpus --year 2024` → writes `evals/corpus/comparison.{json,md}`.
3. `uv run pytest -q` → full suite still green (1 pre-existing skip OK).
4. Read `comparison.md`. Report to the user: the per-question Spearman ρ (Moses-vs-judge agreement), the largest Moses−judge gaps, and any solution where Moses and the judge sharply disagree (these are the calibration signals).

**Commit:**
```bash
git add evals/corpus/moses_scores.json evals/corpus/comparison.json evals/corpus/comparison.md
git commit -m "data(corpus): pilot comparison report for q4/q9/q16"
```

---

## Review
- [x] Code review requested (Tasks 1–2 deterministic code) — both reviewed, compliant, Spearman math traced correct
- [x] All feedback addressed (no blocking issues; missing-year-dir guard accepted as Minor)
- [x] Final verification passed (`uv run pytest` green; `comparison.md` generated with all 3 pilot questions + rank-agreement summary)

## Pilot findings (Phase-1 result)

- Judge validated: `synth_clean` > `synth_primitive` in all 3 questions (88>38, 90>28, 82>48).
- **Moses is systematically too lenient** — nearly every Moses−Judge gap is positive (+0.8 to +64.8).
- Rank agreement is weak: q4 ρ=0.657, q9 ρ=0.3, q16 ρ=0.0.
- Largest divergences are the calibration goldmine: short/incomplete solutions score high on Moses (e.g. q16 `online_1` 51 LOC → Moses 92.8 vs Judge 28: Moses can't see "only Part 1" or copied-recipe over-engineering).
- Single-file scoring inflates small files (few rules fire; DRY finds no dup). A known caveat now quantified.
