"""The autonomous improvement loop (RALPH harness) driver.

Responsibilities, kept deliberately thin so the heavy lifting lives in the shell
harness (``ralph.sh``) and the invariant checker (``check_invariants.py``):

- ``loop_init``  — prepare a working area (a git worktree, or the repo in place),
  drop the loop template (prompt.md, ralph.sh, check_invariants.py) and a seed
  ``campaign.json`` into ``<state-dir>/``, and record the baseline Verdict.
- ``loop_run``   — execute ``ralph.sh`` for up to N iterations / H hours.
- ``loop_check`` — validate ``campaign.json`` against git history and the live
  Verdict (delegates to ``check_invariants.py``).
- ``loop_status``— print a terse one-screen progress summary.

The campaign audit trail (``campaign.json``) is the single source of truth: every
iteration appends a record with the commit, the Score before/after, and the
violation delta. Nothing here calls an LLM directly — that is the harness's job.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path

from .config import Config
from .engine import run as engine_run

TEMPLATE_PACKAGE = "moses.loop_template"
TEMPLATE_FILES = ("prompt.md", "ralph.sh", "check_invariants.py")
CAMPAIGN_FILE = "campaign.json"
SCHEMA_VERSION = 1


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _git(args: list[str], cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )


def _git_ok(args: list[str], cwd: Path) -> str:
    proc = _git(args, cwd)
    if proc.returncode != 0:
        raise LoopError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def _is_git_repo(path: Path) -> bool:
    return _git(["rev-parse", "--is-inside-work-tree"], path).returncode == 0


def _head_commit(path: Path) -> str | None:
    proc = _git(["rev-parse", "HEAD"], path)
    return proc.stdout.strip() if proc.returncode == 0 else None


def _copy_template(state_dir: Path) -> None:
    """Copy the loop template files into the campaign state directory."""
    state_dir.mkdir(parents=True, exist_ok=True)
    pkg = resources.files(TEMPLATE_PACKAGE)
    for name in TEMPLATE_FILES:
        src = pkg / name
        dst = state_dir / name
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
        if name.endswith((".sh", ".py")):
            dst.chmod(0o755)


def _score_of(target: Path, target_path: str, deep: bool = False) -> dict:
    """Return a small Verdict snapshot for the audit trail."""
    judged = target / target_path if target_path else target
    if not judged.exists():
        judged = target
    verdict = engine_run(judged, Config(deep=deep))
    measured = [c for c in verdict.commandments if c.status == "measured"]
    violations = sum(len(c.violations) for c in measured)
    return {
        "score": round(verdict.score, 2),
        "grade": verdict.grade,
        "violations": violations,
        "commandments": {str(c.number): round(c.score_contribution, 2) for c in measured},
        "commit": _head_commit(target),
        "timestamp": _now(),
    }


class LoopError(RuntimeError):
    """Raised for recoverable loop set-up / validation problems."""


@dataclass
class CampaignPaths:
    target: Path
    worktree: Path
    state_dir: Path
    campaign: Path


def default_worktree_path(target: str | Path) -> Path:
    """The default sibling worktree dir for a target repo."""
    target = Path(target).resolve()
    return target.parent / f"{target.name}-moses-loop"


def _resolve_state(worktree: str | Path, state_dir_name: str) -> CampaignPaths:
    wt = Path(worktree).resolve()
    state = wt / state_dir_name
    return CampaignPaths(
        target=wt,
        worktree=wt,
        state_dir=state,
        campaign=state / CAMPAIGN_FILE,
    )


def _load_campaign(campaign_path: Path) -> dict:
    if not campaign_path.exists():
        raise LoopError(f"no campaign at {campaign_path}; run `moses loop init` first")
    return json.loads(campaign_path.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# init
# --------------------------------------------------------------------------- #


def loop_init(
    *,
    target: str | Path,
    branch: str | None = None,
    worktree_path: str | None = None,
    base_ref: str = "HEAD",
    target_path: str = "src/",
    state_dir_name: str = ".moses",
    in_place: bool = False,
) -> str:
    """Prepare a campaign and return a human-readable summary.

    In ``in_place`` mode the loop commits onto the current branch of ``target``.
    Otherwise a dedicated git worktree is created (isolated branch) so the loop
    never touches the user's working tree.
    """
    target = Path(target).resolve()
    if not _is_git_repo(target):
        raise LoopError(f"{target} is not a git repository")

    if in_place:
        worktree = target
    else:
        branch = branch or f"moses/loop-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        worktree = (
            Path(worktree_path).resolve()
            if worktree_path
            else default_worktree_path(target)
        )
        if worktree.exists():
            raise LoopError(f"worktree path already exists: {worktree}")
        _git_ok(["worktree", "add", "-b", branch, str(worktree), base_ref], target)

    state_dir = worktree / state_dir_name
    _copy_template(state_dir)

    baseline = _score_of(worktree, target_path)
    campaign = {
        "schema_version": SCHEMA_VERSION,
        "created": _now(),
        "target_path": target_path,
        "in_place": in_place,
        "branch": branch,
        "base_ref": base_ref,
        "baseline": baseline,
        "best": baseline,
        "iterations": [],
    }
    campaign_path = state_dir / CAMPAIGN_FILE
    campaign_path.write_text(json.dumps(campaign, indent=2) + "\n", encoding="utf-8")

    mode = "in-place" if in_place else f"worktree ({branch})"
    return (
        f"Initialised Moses loop [{mode}]\n"
        f"  worktree:   {worktree}\n"
        f"  state dir:  {state_dir}\n"
        f"  judging:    {target_path}\n"
        f"  baseline:   {baseline['score']} ({baseline['grade']}), "
        f"{baseline['violations']} violations\n"
        f"\nNext: moses loop run --worktree {worktree}"
    )


# --------------------------------------------------------------------------- #
# run
# --------------------------------------------------------------------------- #


def _ralph_path(paths: CampaignPaths) -> Path:
    ralph = paths.state_dir / "ralph.sh"
    if not ralph.exists():
        raise LoopError(f"missing harness: {ralph}; re-run `moses loop init`")
    return ralph


def _loop_env(
    paths: CampaignPaths,
    engine: str,
    max_iterations: int,
    max_hours: float,
    cooldown: int,
) -> dict[str, str]:
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
) -> subprocess.Popen[bytes]:
    """Start the RALPH harness as a background process (non-blocking).

    Returns the Popen handle; the caller owns its lifecycle and must, on exit,
    call ``proc.terminate()`` and then ``proc.wait()`` (or ``proc.communicate()``)
    to reap the child — even if the harness has already finished naturally, an
    unreaped child lingers as a zombie for the caller's lifetime.

    stdin/stdout/stderr are all redirected to ``DEVNULL``: the harness writes its
    own loop.log, and detaching stdin keeps it from competing with the dashboard
    for the terminal.
    """
    paths = _resolve_state(worktree, state_dir_name)
    _load_campaign(paths.campaign)
    ralph = _ralph_path(paths)
    env = _loop_env(paths, engine, max_iterations, max_hours, cooldown)
    return subprocess.Popen(
        ["bash", str(ralph)],
        cwd=str(paths.worktree),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# --------------------------------------------------------------------------- #
# check
# --------------------------------------------------------------------------- #


def loop_check(*, worktree: str | Path, state_dir_name: str = ".moses") -> int:
    """Validate the campaign audit trail. Returns 0 if valid, 1 otherwise."""
    paths = _resolve_state(worktree, state_dir_name)
    campaign = _load_campaign(paths.campaign)

    problems = list(_validate_campaign(campaign, paths))
    if problems:
        for p in problems:
            print(f"FAIL: {p}", file=sys.stderr)
        return 1
    print(f"OK: campaign valid — {len(campaign.get('iterations', []))} iteration(s)")
    return 0


def _validate_campaign(campaign: dict, paths: CampaignPaths):
    """Yield human-readable problem strings; empty means valid."""
    if campaign.get("schema_version") != SCHEMA_VERSION:
        yield f"schema_version {campaign.get('schema_version')} != {SCHEMA_VERSION}"

    baseline = campaign.get("baseline") or {}
    if "score" not in baseline:
        yield "baseline.score missing"

    iterations = campaign.get("iterations", [])
    prev_after = baseline.get("score")
    for i, it in enumerate(iterations):
        idx = it.get("iteration", i)
        for key in ("commit", "score_before", "score_after"):
            if key not in it:
                yield f"iteration {idx}: missing '{key}'"
        commit = it.get("commit")
        if (
            commit
            and _git(["cat-file", "-e", f"{commit}^{{commit}}"], paths.target).returncode != 0
        ):
            yield f"iteration {idx}: commit {commit[:8]} not found in repo"
        # Score continuity: this iteration's score_before should equal the prior
        # iteration's score_after (or the baseline for the first).
        sb = it.get("score_before")
        if prev_after is not None and sb is not None and abs(sb - prev_after) > 0.01:
            yield f"iteration {idx}: score_before {sb} != prior score_after {prev_after}"
        # Violations must never silently increase without a recorded regression flag.
        vb, va = it.get("violations_before"), it.get("violations_after")
        if vb is not None and va is not None and va > vb and not it.get("regression"):
            yield f"iteration {idx}: violations rose {vb}->{va} without regression flag"
        prev_after = it.get("score_after", prev_after)

    best = campaign.get("best") or {}
    if iterations and "score" in best:
        max_after = max(
            (it.get("score_after", baseline.get("score", 0)) for it in iterations),
            default=baseline.get("score", 0),
        )
        if best["score"] < max(max_after, baseline.get("score", 0)) - 0.01:
            yield f"best.score {best['score']} lower than an observed score"


# --------------------------------------------------------------------------- #
# status
# --------------------------------------------------------------------------- #


def loop_status(*, worktree: str | Path, state_dir_name: str = ".moses") -> str:
    """Return a terse progress summary string."""
    paths = _resolve_state(worktree, state_dir_name)
    campaign = _load_campaign(paths.campaign)

    baseline = campaign.get("baseline", {})
    best = campaign.get("best", {})
    iterations = campaign.get("iterations", [])
    last = iterations[-1] if iterations else None

    lines = [
        f"Moses loop @ {paths.worktree}",
        f"  branch:     {campaign.get('branch') or '(in-place)'}",
        f"  baseline:   {baseline.get('score')} ({baseline.get('grade')}), "
        f"{baseline.get('violations')} violations",
        f"  best:       {best.get('score')} ({best.get('grade')})",
        f"  iterations: {len(iterations)}",
    ]
    if last:
        delta = None
        if last.get("score_after") is not None and last.get("score_before") is not None:
            delta = round(last["score_after"] - last["score_before"], 2)
        suffix = ""
        if delta is not None:
            sign = "+" if delta >= 0 else ""
            suffix = f" ({sign}{delta})"
        lines.append(
            f"  last:       #{last.get('iteration')} "
            f"{last.get('score_before')} -> {last.get('score_after')}{suffix}"
        )
    return "\n".join(lines)
