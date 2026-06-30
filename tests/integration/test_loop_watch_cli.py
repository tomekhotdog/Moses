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
        def wait(self, timeout=None): calls["waited"] = True; return 0

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
    # an already-exited child must still be reaped (no zombie)
    assert calls.get("waited") is True


def test_watch_terminates_running_process_on_exit(tmp_path, monkeypatch):
    repo = _git_repo(tmp_path)
    calls = {}

    class FakeProc:
        def poll(self): return None  # still running when the app exits
        def terminate(self): calls["terminated"] = True
        def wait(self, timeout=None): calls["waited"] = True; return 0

    monkeypatch.setattr(loop_runner, "loop_spawn", lambda **k: FakeProc())
    monkeypatch.setattr("moses.loop_tui.MosesLoopApp",
                        type("FakeApp", (), {"__init__": lambda self, **k: None,
                                             "run": lambda self: None}))

    result = CliRunner().invoke(
        cli.main,
        ["loop", "watch", str(repo), "--target-path", "src/", "--in-place"],
    )
    assert result.exit_code == 0, result.output
    assert calls.get("terminated") is True and calls.get("waited") is True
