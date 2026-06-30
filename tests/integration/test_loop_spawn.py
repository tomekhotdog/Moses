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
        def __init__(self, args, cwd=None, env=None, stdin=None, stdout=None, stderr=None):
            captured["args"] = args
            captured["env"] = env
            captured["stdin"] = stdin
            captured["stdout"] = stdout
            captured["stderr"] = stderr
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
    # the harness must not share the terminal with the dashboard
    assert captured["stdin"] == subprocess.DEVNULL
    assert captured["stdout"] == subprocess.DEVNULL
    assert captured["stderr"] == subprocess.DEVNULL
