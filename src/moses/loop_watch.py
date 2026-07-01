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
# matches "C25", "C4" — the Commandment a commit subject targets
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
    number: int | None
    name: str
    score: float


@dataclass(frozen=True)
class CurrentIteration:
    iteration: int
    max_iterations: int
    phase: str
    before_score: float | None
    before_violations: int | None
    started_at: int | None


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
    all_rules: tuple[RuleScore, ...]
    baseline_rules: dict[int, float]
    current: "CurrentIteration | None"
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
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _mtime(p: Path) -> float:
    try:
        return p.stat().st_mtime
    except OSError:
        return 0.0


def _git(args: list[str], cwd: Path) -> str:
    try:
        proc = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, timeout=5
        )
        return proc.stdout if proc.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def _commit_subjects(commits: list[str | None], worktree: Path) -> dict[str, str]:
    """Map each commit -> its subject line in a single git call.

    Robust to missing commits / no repo: a failed git call yields no subjects.
    """
    subjects: dict[str, str] = {}
    hashes = [c for c in commits if c]
    if not hashes:
        return subjects
    out = _git(["log", "--no-walk", "--format=%H%x09%s", *hashes], worktree)
    for line in out.splitlines():
        h, _, subj = line.partition("\t")
        if h and subj:
            subjects[h.strip()] = subj.strip()
    return subjects


def read_log(state_dir: str | Path) -> tuple[str, ...]:
    """The full loop.log as a tuple of lines (empty if absent)."""
    try:
        text = (Path(state_dir) / "loop.log").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ()
    return tuple(text.splitlines())


def _measured_rules(state_dir: Path) -> tuple[RuleScore, ...]:
    """All measured rules from the most recent verdict snapshot, weakest-first."""
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
    """The in-flight iteration from status.json, or None when absent/done."""
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


def read_state(state_dir: str | Path) -> CampaignState:
    """Snapshot the campaign at ``state_dir``. Never raises on malformed input."""
    state_dir = Path(state_dir)
    worktree = state_dir.parent  # the state dir is always .moses/ inside the campaign worktree
    log_tail = read_log(state_dir)[-200:]
    all_rules = _measured_rules(state_dir)
    weakest = all_rules[:6]
    current = _current_iteration(state_dir)
    campaign = _read_json(state_dir / "campaign.json")
    if not campaign:
        return CampaignState(
            exists=False, target_path="", branch=None,
            baseline_score=None, baseline_grade=None,
            best_score=None, best_grade=None,
            rows=(), scores=(), weakest_rules=weakest,
            all_rules=all_rules, baseline_rules={}, current=current,
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

    baseline_rules = {
        int(k): float(v) for k, v in (baseline.get("commandments") or {}).items()
    }

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
        weakest_rules=weakest,
        all_rules=all_rules,
        baseline_rules=baseline_rules,
        current=current,
        log_tail=log_tail,
        last_diffstat=diffstat,
    )
