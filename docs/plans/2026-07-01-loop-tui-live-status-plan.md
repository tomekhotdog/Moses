# Moses Loop TUI — Live Status Enhancements Plan

> **For Claude:** REQUIRED SUB-SKILL: Use tomek-superpowers:build to implement this plan task-by-task.

**Goal:** Add live in-flight status to the loop dashboard: a current-iteration panel (phase/elapsed/spinner), per-rule score movement vs baseline, and a highlighted target + richer diff.
**Architecture:** The harness writes a structured `status.json` per phase; `loop_watch` reads it (+ per-rule baseline) into `CampaignState`; `loop_tui` renders new pure helpers. TUI stays read-only.
**Design:** `docs/plans/2026-07-01-loop-tui-live-status-design.md`

Tests: `uv run pytest`. Commit to `main`. Behaviour preservation: old campaigns (no status.json / no baseline commandments) must still render.

---

### Task A: Harness writes `status.json`; baseline captures per-rule scores  ✅ DONE (a97cf37; guarded 853d74e)
**Depends on:** none

**Files:** Modify `src/moses/loop_template/ralph.sh`, `src/moses/loop_runner.py`; Test: extend `tests/integration/test_loop_harness.py`.

**Step 1 — failing test.** Add to `tests/integration/test_loop_harness.py`:
```python
import json


def test_harness_writes_status_and_baseline_per_rule(inited_repo):
    loop_run(worktree=inited_repo, engine="none",
             max_iterations=1, max_hours=0.0, cooldown=0)
    state = Path(inited_repo) / ".moses"
    status = json.loads((state / "status.json").read_text())
    assert status["phase"] == "done"
    campaign = json.loads((state / "campaign.json").read_text())
    base_rules = campaign["baseline"]["commandments"]
    assert isinstance(base_rules, dict) and base_rules  # per-rule scores captured
```

**Step 2 — run, confirm FAIL** (`uv run pytest tests/integration/test_loop_harness.py` — status.json missing / no baseline commandments).

**Step 3 — implement.**

(a) `loop_runner._score_of`: add a per-rule map (additive key):
```python
    return {
        "score": round(verdict.score, 2),
        "grade": verdict.grade,
        "violations": violations,
        "commandments": {str(c.number): round(c.score_contribution, 2) for c in measured},
        "commit": _head_commit(target),
        "timestamp": _now(),
    }
```

(b) `ralph.sh`: add `STATUS="${STATE_DIR}/status.json"` beside the other path vars, add a `write_status` helper after `log()/die()`, and call it at each phase.

Helper:
```bash
write_status() {
  # $1=phase  $2=before_score(optional)  $3=before_violations(optional)
  python3 - "${STATUS}" "${iteration}" "${MAX_ITERATIONS}" "$1" "${2:-}" "${3:-}" <<'PY'
import json, os, sys, time
path, it, mx, phase, score, viol = sys.argv[1:7]
data = {
    "iteration": int(it) if it else 0,
    "max_iterations": int(mx) if mx else 0,
    "phase": phase,
    "before_score": float(score) if score else None,
    "before_violations": int(viol) if viol else None,
    "started_at": int(time.time()),
}
tmp = path + ".tmp"
with open(tmp, "w") as f:
    json.dump(data, f)
os.replace(tmp, path)
PY
}
```
Calls inside the main `while` loop (map to the existing structure):
- Right after `log "=== iteration ... ==="`: `write_status judging`
- After `before_viol=...; before_commit=...; log "before: ..."`: `write_status engine "${before_score}" "${before_viol}"`
- Immediately before `run_engine`: (already `engine`) — no extra call needed.
- After `run_engine`, before the "did anything change?" check: `write_status verifying "${before_score}" "${before_viol}"`
- In the no-changes branch (before `sleep "${COOLDOWN}"; continue`): `write_status cooldown "${before_score}" "${before_viol}"`
- In the regression branch (before revert/`sleep`): `write_status reverting "${before_score}" "${before_viol}"`
- After a successful commit + record (before final `sleep "${COOLDOWN}"`): `write_status cooldown "${before_score}" "${before_viol}"`
- After the `while` loop ends, before the final `check_invariants validate`: `write_status done`

**Step 4 — run, confirm PASS.** Then full suite `uv run pytest` (expect 194 passed, 1 skipped).

**Step 5 — commit:**
```
git add src/moses/loop_template/ralph.sh src/moses/loop_runner.py tests/integration/test_loop_harness.py
git commit -m "feat(loop): harness emits status.json per phase; baseline captures per-rule scores"
```

---

### Task B: `loop_watch` reads status.json, all-rules, and baseline per-rule  ✅ DONE (20db732; hardened 5a1baaa)
**Depends on:** Task A

**Files:** Modify `src/moses/loop_watch.py`; Test: extend `tests/unit/test_loop_watch.py`.

**Step 1 — failing tests.** Add to `tests/unit/test_loop_watch.py`:
```python
def test_current_iteration_from_status(tmp_path):
    sd = tmp_path / ".moses"
    _write(sd, _campaign())
    (sd / "status.json").write_text(json.dumps({
        "iteration": 2, "max_iterations": 10, "phase": "engine",
        "before_score": 82.0, "before_violations": 94, "started_at": 1719800000,
    }), encoding="utf-8")
    cur = read_state(sd).current
    assert cur is not None and cur.iteration == 2 and cur.phase == "engine"
    assert cur.before_score == 82.0


def test_current_none_when_done_or_missing(tmp_path):
    sd = tmp_path / ".moses"
    _write(sd, _campaign())
    assert read_state(sd).current is None  # no status.json
    (sd / "status.json").write_text(json.dumps({"iteration": 1, "max_iterations": 1,
        "phase": "done", "before_score": None, "before_violations": None,
        "started_at": 1}), encoding="utf-8")
    assert read_state(sd).current is None  # phase == done


def test_all_rules_and_baseline_rules(tmp_path):
    sd = tmp_path / ".moses"
    campaign = _campaign()
    campaign["baseline"]["commandments"] = {"16": 0.0, "12": 90.0, "11": 100.0}
    verdict = {"commandments": [
        {"number": 16, "name": "DRY", "score_contribution": 10.0, "status": "measured"},
        {"number": 12, "name": "Cog", "score_contribution": 100.0, "status": "measured"},
        {"number": 11, "name": "Small", "score_contribution": 100.0, "status": "measured"},
    ]}
    _write(sd, campaign, verdict=verdict)
    s = read_state(sd)
    assert len(s.all_rules) == 3  # not truncated to 6
    assert s.all_rules[0].number == 16  # weakest first
    assert s.baseline_rules == {16: 0.0, 12: 90.0, 11: 100.0}


def test_malformed_status_tolerated(tmp_path):
    sd = tmp_path / ".moses"
    _write(sd, _campaign())
    (sd / "status.json").write_text("{bad", encoding="utf-8")
    assert read_state(sd).current is None  # must not raise
```

**Step 2 — run, confirm FAIL** (no `current`/`all_rules`/`baseline_rules`).

**Step 3 — implement** in `src/moses/loop_watch.py`:

(a) New dataclass:
```python
@dataclass(frozen=True)
class CurrentIteration:
    iteration: int
    max_iterations: int
    phase: str
    before_score: float | None
    before_violations: int | None
    started_at: int | None
```

(b) Add fields to `CampaignState` (after `weakest_rules`):
```python
    all_rules: tuple[RuleScore, ...]
    baseline_rules: dict[int, float]
    current: "CurrentIteration | None"
```

(c) Refactor `_weakest_rules` into `_measured_rules(state_dir)` returning ALL measured rules sorted weakest-first (drop the `[:k]`); derive both lists in `read_state`:
```python
def _measured_rules(state_dir: Path) -> tuple[RuleScore, ...]:
    candidates = [state_dir / "after.json", state_dir / "verdict.json"]
    existing = [p for p in candidates if p.exists()]
    if not existing:
        return ()
    latest = max(existing, key=_mtime)
    verdict = _read_json(latest)
    if not verdict:
        return ()
    measured = [
        RuleScore(c.get("number"), c.get("name", "?"), c.get("score_contribution") or 0.0)
        for c in verdict.get("commandments", [])
        if c.get("status") == "measured"
    ]
    measured.sort(key=lambda r: r.score)
    return tuple(measured)


def _current_iteration(state_dir: Path) -> "CurrentIteration | None":
    data = _read_json(state_dir / "status.json")
    if not data or data.get("phase") == "done":
        return None
    return CurrentIteration(
        iteration=data.get("iteration", 0),
        max_iterations=data.get("max_iterations", 0),
        phase=data.get("phase", ""),
        before_score=data.get("before_score"),
        before_violations=data.get("before_violations"),
        started_at=data.get("started_at"),
    )
```

(d) In `read_state`, compute once and use in BOTH the no-campaign early return and the normal return:
```python
    all_rules = _measured_rules(state_dir)
    weakest = all_rules[:6]
    current = _current_iteration(state_dir)
```
No-campaign branch: pass `weakest_rules=weakest, all_rules=all_rules, baseline_rules={}, current=current`.
Normal branch: `baseline_rules = {int(k): float(v) for k, v in (baseline.get("commandments") or {}).items()}`, and pass `weakest_rules=weakest, all_rules=all_rules, baseline_rules=baseline_rules, current=current`.
Delete the old `_weakest_rules` (replaced by slicing `_measured_rules`).

**Step 4 — run, confirm PASS.** Full suite green (expect 198 passed, 1 skipped).

**Step 5 — commit:**
```
git add src/moses/loop_watch.py tests/unit/test_loop_watch.py
git commit -m "feat(loop): reader exposes current iteration, all rules, baseline per-rule"
```

---

### Task C: dashboard current-iteration panel, per-rule movement, richer diff  ✅ DONE (4295954)
**Depends on:** Task B

**Files:** Modify `src/moses/loop_tui.py`; Test: extend `tests/unit/test_loop_tui.py`.

**Step 1 — failing tests.** Add to `tests/unit/test_loop_tui.py`:
```python
from moses.loop_tui import current_text
from moses.loop_watch import CurrentIteration


def test_current_text_idle_when_none():
    assert "idle" in current_text(None, "", 0, 0).lower()


def test_current_text_shows_phase_and_target():
    cur = CurrentIteration(iteration=4, max_iterations=10, phase="engine",
                           before_score=84.0, before_violations=61, started_at=1)
    out = current_text(cur, "C14 Shallow nesting", 23, 3)
    assert "4/10" in out and "engine" in out and "C14" in out and "23" in out


def test_breakdown_shows_delta_and_target(tmp_path):
    sd = tmp_path / ".moses"
    campaign = _campaign()
    campaign["baseline"]["commandments"] = {"16": 0.0, "12": 100.0}
    verdict = {"commandments": [
        {"number": 16, "name": "DRY", "score_contribution": 10.0, "status": "measured"},
        {"number": 12, "name": "Cog", "score_contribution": 100.0, "status": "measured"},
    ]}
    _write(sd, campaign, verdict=verdict)
    s = read_state(sd)
    out = breakdown_text(s)
    assert "C16" in out and "C12" in out
    assert "+10.0" in out       # 10.0 now vs 0.0 baseline
    assert "◀" in out           # target marker on the weakest (C16)
```
(Keep the existing `test_breakdown_text_lists_weakest`; update it if it asserted the old header — it still checks "C16" and "DRY", which remain present.)

**Step 2 — run, confirm FAIL** (`current_text` missing; breakdown lacks Δ/marker).

**Step 3 — implement** in `src/moses/loop_tui.py`:

(a) Imports: add `import time` and `from textual.containers import Horizontal, Vertical, VerticalScroll`.

(b) Add spinner + `current_text`:
```python
_SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def current_text(current, target: str, elapsed_s: float, frame: int) -> str:
    if current is None:
        return "idle between iterations…"
    spin = _SPINNER[frame % len(_SPINNER)]
    mm, ss = divmod(max(0, int(elapsed_s)), 60)
    before = "—" if current.before_score is None else current.before_score
    return (
        f"[b]Iteration {current.iteration}/{current.max_iterations}[/b]  "
        f"{spin} {current.phase}   {mm:02d}:{ss:02d}\n"
        f"target: {target or '—'}    before: {before}"
    )
```

(c) Rewrite `breakdown_text` to show all rules + Δ + target marker:
```python
def breakdown_text(s: CampaignState) -> str:
    if not s.all_rules:
        return "no verdict yet…"
    target_n = s.all_rules[0].number
    lines = ["[b]Commandments  (score · Δ base)[/b]", ""]
    for r in s.all_rules:
        base = s.baseline_rules.get(r.number)
        delta = "   - " if base is None else f"{r.score - base:+5.1f}"
        marker = " ◀" if r.number == target_n else ""
        lines.append(f"C{r.number:<2} {bar(r.score, 10)} {r.score:5.1f} {delta}  {r.name[:16]}{marker}")
    return "\n".join(lines)
```

(d) `diff_text` gains an optional subject:
```python
def diff_text(diffstat: str, subject: str = "") -> str:
    if not diffstat:
        return ""
    head = f"[b]{escape(subject)}[/b]\n" if subject else "[b]Last change[/b]\n"
    return head + escape(diffstat)
```

(e) App: add `self._frame = 0` in `__init__`. Add the current panel + scrollable breakdown in `compose` (place `#current` right after `#stats`, wrap breakdown in `VerticalScroll`):
```python
        yield Static(id="stats")
        yield Static(id="current")
        with Horizontal(id="middle"):
            with Vertical(id="left"):
                yield DataTable(id="iterations")
                yield Static(id="diff")
            with VerticalScroll(id="right"):
                yield Static(id="breakdown")
```
Add CSS rows: `#current { height: 3; padding: 0 1; }` and keep `#right` styling (VerticalScroll can keep `width: 1fr; border-left: solid $accent;`).

(f) In `refresh_state` (inside the try), advance the frame and render the current panel + enriched diff:
```python
            self._frame += 1
            target = s.all_rules[0].name if s.all_rules else ""
            elapsed = (time.time() - s.current.started_at) if (s.current and s.current.started_at) else 0
            self.query_one("#current", Static).update(current_text(s.current, target, elapsed, self._frame))
            ...
            last_subject = s.rows[-1].subject if s.rows else ""
            self.query_one("#diff", Static).update(diff_text(s.last_diffstat, last_subject))
```
(Replace the old `#diff` update line accordingly; keep the exception guard wrapping the whole body.)

**Step 4 — run, confirm PASS** (`uv run pytest tests/unit/test_loop_tui.py`). Full suite green.

**Step 5 — commit:**
```
git add src/moses/loop_tui.py tests/unit/test_loop_tui.py
git commit -m "feat(loop): dashboard shows live current-iteration, per-rule movement, richer diff"
```

---

### Task D: behaviour preservation + docs
**Depends on:** Task C

**Files:** `docs/spec.md`, `docs/plans/2026-07-01-loop-tui-live-status-plan.md` (mark done).

**Step 1 —** In `docs/spec.md`, near the loop section, note that the harness writes `status.json` (live phase for the dashboard) alongside `campaign.json`.

**Step 2 — full behaviour-preservation run** `uv run pytest` — all green; confirm an OLD-style campaign (no status.json, baseline without `commandments`) still renders: the reader returns `current=None`, `baseline_rules={}`, and `breakdown_text` shows `-` deltas (covered by keeping a test fixture without those keys).

**Step 3 — real smoke** (no engine): init a throwaway repo, `loop_run(engine="none", max_iterations=1)`, then `read_state` and assert `current is None` (phase done) and `all_rules`/`baseline_rules` populated. Then mount `MosesLoopApp` against it (as in the existing async smoke) to confirm the new panels render.

**Step 4 — commit:**
```
git add docs/spec.md docs/plans/2026-07-01-loop-tui-live-status-plan.md
git commit -m "docs: document status.json; mark live-status plan complete"
```

## Review
- [ ] Code review requested (spec + quality per task)
- [ ] All feedback addressed
- [ ] Final verification passed
