"""Loop integration: init -> status -> check, plus check_invariants record/validate."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from moses.loop_runner import loop_check, loop_init, loop_status


def _git(args, cwd):
    subprocess.run(["git", *args], cwd=str(cwd), check=True, capture_output=True)


@pytest.fixture
def temp_repo(tmp_path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(["init", "-q"], repo)
    _git(["config", "user.email", "t@t.co"], repo)
    _git(["config", "user.name", "tester"], repo)
    src = repo / "src"
    src.mkdir()
    (src / "m.py").write_text("def f(a, b, c, d, e):\n    return a\n", encoding="utf-8")
    _git(["add", "-A"], repo)
    _git(["commit", "-qm", "init"], repo)
    return repo


def test_loop_init_in_place(temp_repo):
    summary = loop_init(target=temp_repo, in_place=True, target_path="src/")
    assert "Initialised Moses loop" in summary

    state = temp_repo / ".moses"
    assert (state / "campaign.json").exists()
    assert (state / "ralph.sh").exists()
    assert (state / "check_invariants.py").exists()
    assert (state / "prompt.md").exists()

    campaign = json.loads((state / "campaign.json").read_text())
    assert campaign["schema_version"] == 1
    assert "baseline" in campaign
    assert campaign["iterations"] == []


def test_loop_status_and_check(temp_repo):
    loop_init(target=temp_repo, in_place=True, target_path="src/")
    status = loop_status(worktree=temp_repo)
    assert "Moses loop" in status
    assert "baseline" in status
    assert loop_check(worktree=temp_repo) == 0


def test_check_invariants_record_then_validate(temp_repo):
    loop_init(target=temp_repo, in_place=True, target_path="src/")
    state = temp_repo / ".moses"
    campaign_path = state / "campaign.json"
    checker = state / "check_invariants.py"
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=str(temp_repo), capture_output=True, text=True
    ).stdout.strip()

    base_score = json.loads(campaign_path.read_text())["baseline"]["score"]

    rec = subprocess.run(
        [
            sys.executable, str(checker), "record",
            "--campaign", str(campaign_path),
            "--iteration", "1",
            "--commit", commit,
            "--score-before", str(base_score),
            "--score-after", str(base_score + 5),
            "--violations-before", "3",
            "--violations-after", "1",
            "--grade-after", "B",
        ],
        capture_output=True, text=True,
    )
    assert rec.returncode == 0, rec.stderr

    campaign = json.loads(campaign_path.read_text())
    assert len(campaign["iterations"]) == 1
    assert campaign["best"]["score"] == base_score + 5

    val = subprocess.run(
        [sys.executable, str(checker), "validate",
         "--campaign", str(campaign_path), "--repo", str(temp_repo)],
        capture_output=True, text=True,
    )
    assert val.returncode == 0, val.stderr


def test_check_invariants_detects_bad_commit(temp_repo):
    loop_init(target=temp_repo, in_place=True, target_path="src/")
    state = temp_repo / ".moses"
    campaign_path = state / "campaign.json"
    campaign = json.loads(campaign_path.read_text())
    base_score = campaign["baseline"]["score"]
    campaign["iterations"].append(
        {
            "iteration": 1,
            "commit": "deadbeef" * 5,  # not a real commit
            "score_before": base_score,
            "score_after": base_score + 1,
            "violations_before": 3,
            "violations_after": 3,
            "grade_after": "B",
            "regression": False,
        }
    )
    campaign_path.write_text(json.dumps(campaign), encoding="utf-8")
    # The bogus commit must make validation fail.
    assert loop_check(worktree=temp_repo) == 1
