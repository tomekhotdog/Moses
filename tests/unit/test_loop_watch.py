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
