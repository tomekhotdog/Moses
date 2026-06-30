# Moses Loop TUI Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use tomek-superpowers:build to implement this plan task-by-task.

**Goal:** A `moses loop watch` command that launches a RALPH campaign and renders it live in a Textual dashboard, with `moses loop run` staying headless.
**Architecture:** A pure file reader (`loop_watch.CampaignState`) snapshots the campaign artifacts (`campaign.json`, `loop.log`, `verdict.json`/`after.json`, git); a Textual app (`loop_tui.MosesLoopApp`) polls and renders it; a non-blocking launcher (`loop_runner.loop_spawn`) runs the harness as a supervised subprocess. The TUI is strictly read-only over the ledger.
**Tech Stack:** Python, Textual (optional `[tui]` extra), Rich, Click, pytest (+ pytest-asyncio for the one app smoke test).
**Design:** `docs/plans/2026-06-30-loop-tui-design.md`

Conventions: tests run with `uv run pytest` (sandbox disabled). Behaviour preservation: no commandment/weight/scoring code is touched; existing loop tests stay green.

---

### Task 1: Add the optional `[tui]` dependency

**Depends on:** none

**Files:**
- Modify: `pyproject.toml`

**Step 1: Edit `pyproject.toml`** — add the `tui` extra and pytest-asyncio to dev, and enable async test mode.

In `[project.optional-dependencies]`, add `tui` and extend `dev`:
```toml
[project.optional-dependencies]
dup = ["pygount"]
mutation = ["mutmut"]
tui = ["textual>=0.80"]
dev = ["pytest", "pytest-cov", "pytest-asyncio"]
```

In `[tool.pytest.ini_options]`, add asyncio auto mode (keep existing keys):
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src", "."]
addopts = "-q"
asyncio_mode = "auto"
```

**Step 2: Sync and verify**
Run: `uv sync --extra tui --extra dev`
Then: `uv run python -c "import textual, pytest_asyncio; print('ok')"`
Expected: prints `ok` (pin `textual>=<installed-minor>` in pyproject to the actual resolved version if it is newer than 0.80).

**Step 3: Verify the suite still green**
Run: `uv run pytest`
Expected: `171 passed, 1 skipped` (unchanged).

**Step 4: Commit**
```bash
git add pyproject.toml uv.lock
git commit -m "build(tui): add optional textual extra + async test mode"
```

---

### Task 2: `CampaignState` — the pure campaign reader

**Depends on:** none

**Files:**
- Create: `src/moses/loop_watch.py`
- Test: `tests/unit/test_loop_watch.py`

**Step 1: Write the failing test**
```python
"""loop_watch: a pure, partial-file-tolerant reader of campaign state."""

from __future__ import annotations

import json
from pathlib import Path

from moses.loop_watch import read_state, read_log, sparkline


def _write(state_dir: Path, campaign: dict, log: str = "", verdict: dict | None = None):
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / "campaign.json").write_text(json.dumps(campaign), encoding="utf-8")
    if log:
        (state_dir / "loop.log").write_text(log, encoding="utf-8")
    if verdict is not None:
        (state_dir / "verdict.json").write_text(json.dumps(verdict), encoding="utf-8")


def _campaign() -> dict:
    return {
        "schema_version": 1,
        "target_path": "src/",
        "branch": "moses/loop-x",
        "baseline": {"score": 80.0, "grade": "B", "violations": 100},
        "best": {"score": 84.0, "grade": "A"},
        "iterations": [
            {"iteration": 1, "score_before": 80.0, "score_after": 82.0,
             "violations_before": 100, "violations_after": 94, "grade_after": "B",
             "commit": "abc123"},
            {"iteration": 2, "score_before": 82.0, "score_after": 84.0,
             "violations_before": 94, "violations_after": 90, "grade_after": "A",
             "commit": "def456"},
        ],
    }


def test_sparkline_handles_empty_and_flat():
    assert sparkline([]) == ""
    assert sparkline([5.0, 5.0, 5.0]) == "▁▁▁"


def test_read_state_parses_rows_and_scores(tmp_path):
    sd = tmp_path / ".moses"
    _write(sd, _campaign())
    s = read_state(sd)
    assert s.exists is True
    assert s.target_path == "src/"
    assert s.baseline_score == 80.0 and s.best_score == 84.0
    assert [r.iteration for r in s.rows] == [1, 2]
    assert s.scores == (80.0, 82.0, 84.0)
    assert s.total_gain == 4.0
    assert len(s.sparkline) == 3


def test_summary_counts_improving(tmp_path):
    sd = tmp_path / ".moses"
    _write(sd, _campaign())
    summ = read_state(sd).summary
    assert summ.iterations == 2
    assert summ.improving == 2 and summ.regressing == 0
    assert summ.total_gain == 4.0


def test_weakest_rules_from_verdict(tmp_path):
    sd = tmp_path / ".moses"
    verdict = {"commandments": [
        {"number": 16, "name": "DRY", "score_contribution": 0.0, "status": "measured"},
        {"number": 12, "name": "Low cognitive complexity", "score_contribution": 100.0, "status": "measured"},
        {"number": 4, "name": "Layers", "score_contribution": None, "status": "not_measured"},
    ]}
    _write(sd, _campaign(), verdict=verdict)
    s = read_state(sd)
    assert s.weakest_rules[0].number == 16 and s.weakest_rules[0].score == 0.0
    assert all(r.number != 4 for r in s.weakest_rules)  # not_measured excluded


def test_log_tail_and_read_log(tmp_path):
    sd = tmp_path / ".moses"
    _write(sd, _campaign(), log="line1\nline2\nline3\n")
    assert read_log(sd) == ("line1", "line2", "line3")
    assert read_state(sd).log_tail[-1] == "line3"


def test_missing_campaign_is_not_exists(tmp_path):
    sd = tmp_path / ".moses"
    sd.mkdir()
    assert read_state(sd).exists is False


def test_malformed_campaign_does_not_raise(tmp_path):
    sd = tmp_path / ".moses"
    sd.mkdir()
    (sd / "campaign.json").write_text("{not json", encoding="utf-8")
    s = read_state(sd)  # must not raise
    assert s.exists is False


def test_commandment_parsed_from_commit_subject_absent_without_git(tmp_path):
    # No git repo at tmp_path -> subjects empty -> commandment falls back to "—".
    sd = tmp_path / ".moses"
    _write(sd, _campaign())
    assert all(r.commandment == "—" for r in read_state(sd).rows)
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_loop_watch.py`
Expected: FAIL (`ModuleNotFoundError: moses.loop_watch`).

**Step 3: Write the implementation**
```python
"""Read a Moses loop campaign's live state for display.

A pure reader over the artifacts the RALPH harness writes incrementally
(`campaign.json`, `loop.log`, `verdict.json`/`after.json`, git). Returns an
immutable `CampaignState` snapshot. Tolerant of partial, missing, or mid-append
files — never raises on a malformed read — so a UI polling this while the loop
writes can render safely.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

_BLOCKS = "▁▂▃▄▅▆▇█"
_CMD_RE = re.compile(r"\bC(\d+)\b")


def sparkline(values: list[float]) -> str:
    """ASCII sparkline of a numeric series (shared with the offline reporter)."""
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        return _BLOCKS[0] * len(values)
    out = []
    for v in values:
        idx = int((v - lo) / (hi - lo) * (len(_BLOCKS) - 1))
        out.append(_BLOCKS[idx])
    return "".join(out)


@dataclass(frozen=True)
class RuleScore:
    number: int
    name: str
    score: float


@dataclass(frozen=True)
class IterationRow:
    iteration: int
    score_before: float | None
    score_after: float | None
    violations_before: int | None
    violations_after: int | None
    grade_after: str | None
    regression: bool
    commit: str | None
    subject: str
    commandment: str  # "C25" or "—"


@dataclass(frozen=True)
class CampaignSummary:
    baseline_score: float
    final_score: float
    best_score: float | None
    total_gain: float
    iterations: int
    improving: int
    regressing: int


@dataclass(frozen=True)
class CampaignState:
    exists: bool
    target_path: str
    branch: str | None
    baseline_score: float | None
    baseline_grade: str | None
    best_score: float | None
    best_grade: str | None
    rows: tuple[IterationRow, ...]
    scores: tuple[float, ...]
    weakest_rules: tuple[RuleScore, ...]
    log_tail: tuple[str, ...]
    last_diffstat: str

    @property
    def sparkline(self) -> str:
        return sparkline(list(self.scores))

    @property
    def total_gain(self) -> float:
        if not self.scores:
            return 0.0
        return round(self.scores[-1] - self.scores[0], 2)

    @property
    def final_score(self) -> float | None:
        return self.scores[-1] if self.scores else self.baseline_score

    @property
    def summary(self) -> CampaignSummary:
        base = self.scores[0] if self.scores else (self.baseline_score or 0.0)
        final = self.scores[-1] if self.scores else base
        deltas = [
            r.score_after - r.score_before
            for r in self.rows
            if r.score_after is not None and r.score_before is not None
        ]
        return CampaignSummary(
            baseline_score=round(base, 2),
            final_score=round(final, 2),
            best_score=self.best_score,
            total_gain=round(final - base, 2),
            iterations=len(self.rows),
            improving=sum(1 for d in deltas if d > 0),
            regressing=sum(1 for d in deltas if d < 0),
        )


def _read_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _git(args: list[str], cwd: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(cwd), capture_output=True, text=True, timeout=5
        )
        return proc.stdout if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _commit_subjects(commits: list[str | None], worktree: Path) -> dict[str, str]:
    """Map each commit -> its subject line. Robust to missing commits / no repo."""
    subjects: dict[str, str] = {}
    for c in [c for c in commits if c]:
        out = _git(["show", "-s", "--format=%s", c], worktree).strip()
        if out:
            subjects[c] = out.splitlines()[0]
    return subjects


def read_log(state_dir: str | Path) -> tuple[str, ...]:
    """The full loop.log as a tuple of lines (empty if absent)."""
    try:
        text = (Path(state_dir) / "loop.log").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ()
    return tuple(text.splitlines())


def _weakest_rules(state_dir: Path, k: int = 6) -> tuple[RuleScore, ...]:
    """Lowest-scoring measured rules from the most recent verdict snapshot."""
    candidates = [state_dir / "after.json", state_dir / "verdict.json"]
    existing = [p for p in candidates if p.exists()]
    if not existing:
        return ()
    latest = max(existing, key=lambda p: p.stat().st_mtime)
    verdict = _read_json(latest)
    if not verdict:
        return ()
    measured = [
        RuleScore(c.get("number"), c.get("name", "?"), c.get("score_contribution") or 0.0)
        for c in verdict.get("commandments", [])
        if c.get("status") == "measured"
    ]
    measured.sort(key=lambda r: r.score)
    return tuple(measured[:k])


def read_state(state_dir: str | Path) -> CampaignState:
    """Snapshot the campaign at ``state_dir``. Never raises on malformed input."""
    state_dir = Path(state_dir)
    worktree = state_dir.parent
    log_tail = read_log(state_dir)[-200:]
    campaign = _read_json(state_dir / "campaign.json")
    if not campaign:
        return CampaignState(
            exists=False, target_path="", branch=None,
            baseline_score=None, baseline_grade=None,
            best_score=None, best_grade=None,
            rows=(), scores=(), weakest_rules=_weakest_rules(state_dir),
            log_tail=log_tail, last_diffstat="",
        )

    baseline = campaign.get("baseline") or {}
    best = campaign.get("best") or {}
    iterations = campaign.get("iterations") or []

    commits = [it.get("commit") for it in iterations]
    subjects = _commit_subjects(commits, worktree)

    rows = []
    for it in iterations:
        commit = it.get("commit")
        subject = subjects.get(commit, "")
        m = _CMD_RE.search(subject or "")
        rows.append(IterationRow(
            iteration=it.get("iteration", 0),
            score_before=it.get("score_before"),
            score_after=it.get("score_after"),
            violations_before=it.get("violations_before"),
            violations_after=it.get("violations_after"),
            grade_after=it.get("grade_after"),
            regression=bool(it.get("regression")),
            commit=commit,
            subject=subject,
            commandment=f"C{m.group(1)}" if m else "—",
        ))

    scores: list[float] = []
    if baseline.get("score") is not None:
        scores.append(baseline["score"])
    for it in iterations:
        if it.get("score_after") is not None:
            scores.append(it["score_after"])

    last_commit = next((c for c in reversed(commits) if c), None)
    diffstat = ""
    if last_commit:
        diffstat = _git(["show", "--stat", "--format=", last_commit], worktree).strip()

    return CampaignState(
        exists=True,
        target_path=campaign.get("target_path", "src/"),
        branch=campaign.get("branch"),
        baseline_score=baseline.get("score"),
        baseline_grade=baseline.get("grade"),
        best_score=best.get("score"),
        best_grade=best.get("grade"),
        rows=tuple(rows),
        scores=tuple(scores),
        weakest_rules=_weakest_rules(state_dir),
        log_tail=log_tail,
        last_diffstat=diffstat,
    )
```

**Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_loop_watch.py`
Expected: PASS (8 passed).

**Step 5: Commit**
```bash
git add src/moses/loop_watch.py tests/unit/test_loop_watch.py
git commit -m "feat(loop): CampaignState reader for live dashboard"
```

---

### Task 3: Non-blocking launcher (`loop_spawn`) + shared env

**Depends on:** none (can run parallel with Task 2)

**Files:**
- Modify: `src/moses/loop_runner.py`
- Test: `tests/integration/test_loop_spawn.py`

**Step 1: Write the failing test**
```python
"""loop_spawn: start the RALPH harness as a supervised background process."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from moses import loop_runner
from moses.loop_runner import default_worktree_path, loop_init, loop_spawn


@pytest.fixture
def inited_repo(tmp_path):
    repo = tmp_path / "proj"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "m.py").write_text("def f(x):\n    return x\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], cwd=repo, check=True)
    loop_init(target=repo, target_path="src/", in_place=True)
    return repo


def test_default_worktree_path():
    p = default_worktree_path("/a/b/proj")
    assert p.name == "proj-moses-loop" and p.parent == Path("/a/b")


def test_loop_spawn_builds_env_and_is_nonblocking(inited_repo, monkeypatch):
    captured = {}

    class FakePopen:
        def __init__(self, args, cwd=None, env=None, stdout=None, stderr=None):
            captured["args"] = args
            captured["env"] = env
            self.returncode = None

        def poll(self):
            return None

    monkeypatch.setattr(loop_runner.subprocess, "Popen", FakePopen)
    proc = loop_spawn(worktree=inited_repo, state_dir_name=".moses",
                      engine="claude", max_iterations=7, cooldown=1)
    assert proc.poll() is None  # non-blocking: returns immediately
    assert captured["args"][0] == "bash"
    assert captured["env"]["MOSES_MAX_ITERATIONS"] == "7"
    assert captured["env"]["MOSES_ENGINE"] == "claude"
    assert "MOSES_BIN" in captured["env"]
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest tests/integration/test_loop_spawn.py`
Expected: FAIL (`ImportError: cannot import name 'loop_spawn'`).

**Step 3: Implement** — in `src/moses/loop_runner.py`:

(a) Add a shared worktree-path helper near `_resolve_state`:
```python
def default_worktree_path(target: str | Path) -> Path:
    """The default sibling worktree dir for a target repo."""
    target = Path(target).resolve()
    return target.parent / f"{target.name}-moses-loop"
```

(b) Replace the inline default in `loop_init` (the `worktree = (...)` assignment) with the helper:
```python
        worktree = (
            Path(worktree_path).resolve()
            if worktree_path
            else default_worktree_path(target)
        )
```

(c) Extract env-building + harness-path helpers and refactor `loop_run`; add `loop_spawn`. Replace the existing `loop_run` body region with:
```python
def _ralph_path(paths: CampaignPaths) -> Path:
    ralph = paths.state_dir / "ralph.sh"
    if not ralph.exists():
        raise LoopError(f"missing harness: {ralph}; re-run `moses loop init`")
    return ralph


def _loop_env(
    paths: CampaignPaths, engine: str, max_iterations: int, max_hours: float, cooldown: int
) -> dict:
    env = dict(os.environ)
    env.update(
        {
            "MOSES_WORKTREE": str(paths.worktree),
            "MOSES_STATE_DIR": str(paths.state_dir),
            "MOSES_ENGINE": engine,
            "MOSES_MAX_ITERATIONS": str(max_iterations),
            "MOSES_MAX_HOURS": str(max_hours),
            "MOSES_COOLDOWN": str(cooldown),
            "MOSES_BIN": shutil.which("moses") or sys.executable,
        }
    )
    return env


def loop_run(
    *,
    worktree: str | Path,
    state_dir_name: str = ".moses",
    engine: str = "auto",
    max_iterations: int = 10,
    max_hours: float = 0.0,
    cooldown: int = 5,
) -> int:
    """Execute the RALPH harness (blocking). Returns the harness exit code."""
    paths = _resolve_state(worktree, state_dir_name)
    _load_campaign(paths.campaign)  # fail fast if not initialised
    ralph = _ralph_path(paths)
    env = _loop_env(paths, engine, max_iterations, max_hours, cooldown)
    proc = subprocess.run(["bash", str(ralph)], cwd=str(paths.worktree), env=env)
    return proc.returncode


def loop_spawn(
    *,
    worktree: str | Path,
    state_dir_name: str = ".moses",
    engine: str = "auto",
    max_iterations: int = 10,
    max_hours: float = 0.0,
    cooldown: int = 5,
) -> subprocess.Popen:
    """Start the RALPH harness as a background process (non-blocking).

    Returns the Popen handle; the caller supervises it and must terminate it on
    exit. The harness writes its own loop.log, so stdout/stderr are discarded to
    keep the terminal clean for the dashboard.
    """
    paths = _resolve_state(worktree, state_dir_name)
    _load_campaign(paths.campaign)
    ralph = _ralph_path(paths)
    env = _loop_env(paths, engine, max_iterations, max_hours, cooldown)
    return subprocess.Popen(
        ["bash", str(ralph)],
        cwd=str(paths.worktree),
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
```
(Remove the now-duplicated env block from the old `loop_run`.)

**Step 4: Run tests to verify pass**
Run: `uv run pytest tests/integration/test_loop_spawn.py tests/integration/test_loop.py`
Expected: PASS (existing loop tests still green; new spawn tests pass).

**Step 5: Commit**
```bash
git add src/moses/loop_runner.py tests/integration/test_loop_spawn.py
git commit -m "feat(loop): non-blocking loop_spawn + shared env helper"
```

---

### Task 4: `MosesLoopApp` — the Textual dashboard

**Depends on:** Task 1 (textual), Task 2 (CampaignState)

**Files:**
- Create: `src/moses/loop_tui.py`
- Test: `tests/unit/test_loop_tui.py`

**Step 1: Write the failing test** (pure render helpers tested sync; one async smoke test)
```python
"""loop_tui: pure render helpers + a Textual smoke test."""

from __future__ import annotations

import json
from pathlib import Path

from moses.loop_tui import MosesLoopApp, bar, breakdown_text, stats_text
from moses.loop_watch import read_state


def _fixture(tmp_path: Path) -> Path:
    sd = tmp_path / ".moses"
    sd.mkdir(parents=True)
    (sd / "campaign.json").write_text(json.dumps({
        "target_path": "src/", "branch": "moses/loop-x",
        "baseline": {"score": 80.0, "grade": "B", "violations": 100},
        "best": {"score": 84.0, "grade": "A"},
        "iterations": [
            {"iteration": 1, "score_before": 80.0, "score_after": 84.0,
             "violations_before": 100, "violations_after": 90, "grade_after": "A",
             "commit": "abc"},
        ],
    }), encoding="utf-8")
    (sd / "loop.log").write_text("hello\nworld\n", encoding="utf-8")
    (sd / "verdict.json").write_text(json.dumps({"commandments": [
        {"number": 16, "name": "DRY", "score_contribution": 0.0, "status": "measured"},
    ]}), encoding="utf-8")
    return sd


def test_bar_fills_proportionally():
    assert bar(100, width=10) == "█" * 10
    assert bar(0, width=10) == "·" * 10
    assert bar(50, width=10).count("█") == 5


def test_stats_text_includes_key_numbers(tmp_path):
    s = read_state(_fixture(tmp_path))
    text = stats_text(s, max_iterations=10)
    assert "80.0" in text and "84.0" in text and "1/10" in text


def test_breakdown_text_lists_weakest(tmp_path):
    s = read_state(_fixture(tmp_path))
    assert "C16" in breakdown_text(s) and "DRY" in breakdown_text(s)


async def test_app_mounts_and_renders(tmp_path):
    sd = _fixture(tmp_path)
    app = MosesLoopApp(state_dir=sd, max_iterations=10, process=None)
    async with app.run_test() as pilot:
        await pilot.pause()
        from textual.widgets import Static
        stats = app.query_one("#stats", Static)
        assert "baseline" in str(stats.renderable)
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest tests/unit/test_loop_tui.py`
Expected: FAIL (`ModuleNotFoundError: moses.loop_tui`).

**Step 3: Implement** `src/moses/loop_tui.py`:
```python
"""Textual dashboard for a live Moses loop campaign.

`MosesLoopApp` polls `loop_watch.read_state` on a timer and renders the campaign:
header stats, score sparkline, an iterations table, the weakest-commandment
breakdown, the latest diff, and a live log tail. On completion it shows a summary
screen. Strictly read-only over the ledger; the supervised subprocess (if any) is
terminated by the caller.

Render logic is split into pure module functions (`stats_text`, `breakdown_text`,
`bar`) so it is unit-testable without an event loop.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Log, Static

from .loop_watch import CampaignState, read_log, read_state


def bar(score: float, width: int = 20) -> str:
    filled = int(round(max(0.0, min(100.0, score)) / 100 * width))
    return "█" * filled + "·" * (width - filled)


def stats_text(s: CampaignState, max_iterations: int) -> str:
    if not s.exists:
        return "waiting for campaign…"
    done = len(s.rows)
    gain = s.total_gain
    sign = "+" if gain >= 0 else ""
    final = s.final_score
    return (
        f"baseline {s.baseline_score} {s.baseline_grade or ''}    "
        f"best {s.best_score} {s.best_grade or ''}    "
        f"iter {done}/{max_iterations}\n"
        f"Score {s.sparkline}  {s.baseline_score}→{final} ({sign}{gain})"
    )


def breakdown_text(s: CampaignState) -> str:
    if not s.weakest_rules:
        return "no verdict yet…"
    lines = ["[b]Weakest commandments[/b]", ""]
    for r in s.weakest_rules:
        lines.append(f"C{r.number:<2} {bar(r.score)} {r.score:5.1f}  {r.name[:20]}")
    return "\n".join(lines)


class SummaryScreen(Screen):
    BINDINGS = [("q", "app.quit", "Quit")]

    def __init__(self, state: CampaignState) -> None:
        super().__init__()
        self._summary = state.summary
        self._spark = state.sparkline

    def compose(self) -> ComposeResult:
        s = self._summary
        body = (
            "[b]Campaign complete[/b]\n\n"
            f"baseline   {s.baseline_score}\n"
            f"final      {s.final_score}\n"
            f"best       {s.best_score}\n"
            f"total gain {s.total_gain:+}\n"
            f"iterations {s.iterations} ({s.improving} up, {s.regressing} down)\n"
            f"trajectory {self._spark}\n\n"
            "[dim]press q to quit[/dim]"
        )
        yield Header()
        yield Static(body, id="summary")
        yield Footer()


class MosesLoopApp(App):
    CSS = """
    #stats { height: 4; padding: 0 1; border-bottom: solid $accent; }
    #middle { height: 1fr; }
    #left { width: 2fr; }
    #right { width: 1fr; border-left: solid $accent; }
    #iterations { height: 2fr; }
    #diff { height: 1fr; padding: 0 1; }
    #breakdown { padding: 0 1; }
    #log { height: 10; border-top: solid $accent; }
    """
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("up", "scroll_log(-1)", "Scroll log"),
        ("down", "scroll_log(1)", "Scroll log"),
    ]

    def __init__(self, *, state_dir, max_iterations: int, process=None, poll: float = 0.7):
        super().__init__()
        self._state_dir = Path(state_dir)
        self._max_iterations = max_iterations
        self._process = process
        self._poll = poll
        self._log_seen = 0
        self._finished = False

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="stats")
        with Horizontal(id="middle"):
            with Vertical(id="left"):
                yield DataTable(id="iterations")
                yield Static(id="diff")
            with Vertical(id="right"):
                yield Static(id="breakdown")
        yield Log(id="log", highlight=False)
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#iterations", DataTable)
        table.add_columns("#", "Cmd", "Before", "After", "ΔViol", "")
        self.refresh_state()
        self.set_interval(self._poll, self.refresh_state)

    def refresh_state(self) -> None:
        s = read_state(self._state_dir)
        self.query_one("#stats", Static).update(stats_text(s, self._max_iterations))
        self._render_table(s)
        self.query_one("#breakdown", Static).update(breakdown_text(s))
        self.query_one("#diff", Static).update(
            ("[b]Last change[/b]\n" + s.last_diffstat) if s.last_diffstat else ""
        )
        self._render_log()
        if not self._finished and self._process is not None and self._process.poll() is not None:
            self._finished = True
            self.refresh_state()  # final pull before summary
            self.push_screen(SummaryScreen(s))

    def _render_table(self, s: CampaignState) -> None:
        table = self.query_one("#iterations", DataTable)
        table.clear()
        for r in s.rows:
            mark = "revert" if r.regression else "✓"
            if r.violations_after is None or r.violations_before is None:
                dv = ""
            else:
                dv = f"{r.violations_after - r.violations_before:+d}"
            table.add_row(str(r.iteration), r.commandment,
                          str(r.score_before), str(r.score_after), dv, mark)

    def _render_log(self) -> None:
        lines = read_log(self._state_dir)
        log = self.query_one("#log", Log)
        for line in lines[self._log_seen:]:
            log.write_line(line)
        self._log_seen = len(lines)

    def action_scroll_log(self, delta: int) -> None:
        log = self.query_one("#log", Log)
        log.scroll_relative(y=delta)
```

**Step 4: Run test to verify it passes**
Run: `uv run pytest tests/unit/test_loop_tui.py`
Expected: PASS (4 passed; the async test runs under `asyncio_mode=auto`).

**Step 5: Commit**
```bash
git add src/moses/loop_tui.py tests/unit/test_loop_tui.py
git commit -m "feat(loop): Textual dashboard app (MosesLoopApp)"
```

---

### Task 5: `moses loop watch` CLI command

**Depends on:** Task 2, Task 3, Task 4

**Files:**
- Modify: `src/moses/cli.py`
- Test: `tests/integration/test_loop_watch_cli.py`

**Step 1: Write the failing test**
```python
"""loop watch CLI: auto-init + spawn + app wiring (subprocess & app mocked)."""

from __future__ import annotations

import subprocess

from click.testing import CliRunner

from moses import cli, loop_runner


def _git_repo(tmp_path):
    repo = tmp_path / "proj"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "m.py").write_text("def f(x):\n    return x\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], cwd=repo, check=True)
    return repo


def test_watch_auto_inits_spawns_and_runs(tmp_path, monkeypatch):
    repo = _git_repo(tmp_path)
    calls = {}

    class FakeProc:
        def poll(self): return 0
        def terminate(self): calls["terminated"] = True
        def wait(self, timeout=None): return 0

    def fake_spawn(**kwargs):
        calls["spawn"] = kwargs
        return FakeProc()

    class FakeApp:
        def __init__(self, **kwargs): calls["app"] = kwargs
        def run(self): calls["ran"] = True

    monkeypatch.setattr(loop_runner, "loop_spawn", fake_spawn)
    monkeypatch.setattr("moses.loop_tui.MosesLoopApp", FakeApp)

    result = CliRunner().invoke(
        cli.main,
        ["loop", "watch", str(repo), "--target-path", "src/", "--in-place",
         "--max-iterations", "3"],
    )
    assert result.exit_code == 0, result.output
    assert calls["ran"] is True
    assert calls["spawn"]["max_iterations"] == 3
    assert calls["app"]["max_iterations"] == 3
```

**Step 2: Run test to verify it fails**
Run: `uv run pytest tests/integration/test_loop_watch_cli.py`
Expected: FAIL (no `watch` subcommand).

**Step 3: Implement** — add to `src/moses/cli.py` after `loop_run_cmd` (note `--in-place` so the test/self-run can avoid creating sibling worktrees; default is worktree mode):
```python
@loop.command("watch")
@click.argument("target", required=False, type=click.Path(exists=True))
@click.option("--worktree", "worktree", default=None, type=click.Path(),
              help="Existing campaign worktree (skip auto-init).")
@click.option("--target-path", default="src/", help="Path within the repo to judge.")
@click.option("--in-place", is_flag=True, help="Auto-init onto the current branch.")
@click.option("--state-dir", "state_dir", default=".moses")
@click.option("--engine", default="auto", type=click.Choice(["auto", "claude", "codex"]))
@click.option("--max-iterations", default=10, type=int)
@click.option("--max-hours", default=0.0, type=float)
@click.option("--cooldown", default=5, type=int)
def loop_watch_cmd(target, worktree, target_path, in_place, state_dir, engine,
                   max_iterations, max_hours, cooldown):
    """Launch a campaign and watch it live in a terminal dashboard.

    Pass TARGET to auto-init a campaign (worktree mode unless --in-place), or
    --worktree to attach to an existing one.
    """
    from . import loop_runner
    from .loop_runner import (
        LoopError, default_worktree_path, loop_init, _resolve_state,
    )

    if worktree is None:
        if target is None:
            raise SystemExit("provide TARGET (to auto-init) or --worktree (existing campaign)")
        paths = _resolve_state(
            target if in_place else default_worktree_path(target), state_dir
        )
        if not paths.campaign.exists():
            try:
                click.echo(loop_init(
                    target=target, target_path=target_path,
                    state_dir_name=state_dir, in_place=in_place,
                ))
            except LoopError as exc:
                raise SystemExit(str(exc))
        worktree = str(paths.worktree)

    paths = _resolve_state(worktree, state_dir)
    if not paths.campaign.exists():
        raise SystemExit(f"no campaign at {paths.campaign}; run `moses loop init` first")

    try:
        from .loop_tui import MosesLoopApp
    except ImportError:
        raise SystemExit("The loop dashboard needs Textual:\n  uv pip install 'moses[tui]'")

    proc = loop_runner.loop_spawn(
        worktree=worktree, state_dir_name=state_dir, engine=engine,
        max_iterations=max_iterations, max_hours=max_hours, cooldown=cooldown,
    )
    try:
        MosesLoopApp(state_dir=paths.state_dir, max_iterations=max_iterations,
                     process=proc).run()
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
```
Ensure `import subprocess` and `import sys` are present at the top of `cli.py` (add `import subprocess` if missing).

**Step 4: Run tests to verify pass**
Run: `uv run pytest tests/integration/test_loop_watch_cli.py`
Expected: PASS (1 passed).

**Step 5: Commit**
```bash
git add src/moses/cli.py tests/integration/test_loop_watch_cli.py
git commit -m "feat(cli): moses loop watch — launch + live dashboard"
```

---

### Task 6: Behaviour preservation, docs, and offline-reporter dedup

**Depends on:** Task 2, Task 5

**Files:**
- Modify: `evals/build_per_iter_presentation.py` (import shared `sparkline`)
- Modify: `docs/spec.md` (document `moses loop watch`)
- Modify: `docs/language.md` (add Dashboard term)

**Step 1: Dedup the sparkline** — make `evals/build_per_iter_presentation.py` import the package copy instead of redefining it. Replace its local `_BLOCKS`/`sparkline` definition with:
```python
from moses.loop_watch import sparkline  # single source of truth
```
(Delete the now-redundant `_BLOCKS` constant and local `sparkline` function.)

**Step 2: Verify the reporter still works**
Run: `uv run python -c "from evals.build_per_iter_presentation import build; print(build({'baseline':{'score':80,'grade':'B'},'best':{'score':84,'grade':'A'},'iterations':[]})[:40])"`
Expected: prints the start of the Markdown (`# Moses Campaign — Per-Iteration…`), no ImportError.

**Step 3: Document** — in `docs/spec.md`, add to the loop commands block:
```
moses loop watch <target>             # launch + live Textual dashboard
```
and in `docs/language.md` add a row:
```
| **Dashboard** | The live Textual view of a running campaign (`moses loop watch`); a read-only renderer of campaign.json/loop.log. |
```

**Step 4: Full behaviour-preservation run**
Run: `uv run pytest`
Expected: all prior tests pass plus the new ones (loop_watch, loop_spawn, loop_tui, loop_watch_cli). No failures; `moses loop run` unchanged.

**Step 5: End-to-end smoke (no engine needed)** — verify `watch` renders a real harness with engine=`none`-style no-op by confirming the reader + app handle a freshly-inited campaign. Manual check (documented, not asserted in CI):
```bash
# from a scratch dir, against a throwaway copy — confirms the dashboard launches.
# Real self-run is the separate gated step below.
```

**Step 6: Commit**
```bash
git add evals/build_per_iter_presentation.py docs/spec.md docs/language.md
git commit -m "docs+refactor: document loop watch; share sparkline source"
```

---

### Post-plan: the real self-run (gated, not a code task)

After all tasks land and the suite is green, run the dashboard on Moses itself:
```bash
uv run moses loop watch . --target-path src/moses --max-iterations 10
```
This auto-inits a `Moses-moses-loop` worktree on a fresh branch, spawns the RALPH harness (engine=claude), and renders live. Watch C16/C25 climb. On completion, write the presentation:
```bash
uv run python evals/build_per_iter_presentation.py ../Moses-moses-loop/.moses/campaign.json -o loop-report.md
```
Confirm with the user before launching (autonomous commits + claude subprocesses).

## Review
- [ ] Code review requested
- [ ] All feedback addressed
- [ ] Final verification passed
