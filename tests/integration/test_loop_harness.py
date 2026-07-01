"""The RALPH harness (ralph.sh) actually enters its iteration loop.

Regression guard for the bug where a default ``--max-hours 0.0`` was passed to
the harness as the string ``"0.0"`` — the old ``[ "$MAX_HOURS" = "0" ]`` check
missed it, computed a zero budget, and the loop exited "time budget reached"
before iteration 1. Uses ``engine=none`` so no coding engine is required.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from moses.loop_runner import loop_init, loop_run


@pytest.fixture
def inited_repo(tmp_path):
    repo = tmp_path / "proj"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "m.py").write_text("def add(a, b):\n    return a + b\n", encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t",
                    "commit", "-qm", "init"], cwd=repo, check=True)
    loop_init(target=repo, target_path="src/", in_place=True)
    return repo


def test_harness_enters_loop_with_default_unlimited_hours(inited_repo):
    # max_hours=0.0 means "unlimited": the harness must run the iteration, not
    # exit at iteration 0 with "time budget reached".
    code = loop_run(
        worktree=inited_repo, engine="none",
        max_iterations=1, max_hours=0.0, cooldown=0,
    )
    log = (Path(inited_repo) / ".moses" / "loop.log").read_text(encoding="utf-8")
    assert "iteration 1/1" in log, log
    assert "time budget reached" not in log, log
    assert code == 0
