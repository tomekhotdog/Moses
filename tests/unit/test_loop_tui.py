"""loop_tui: pure render helpers + a Textual smoke test."""

from __future__ import annotations

import json
from pathlib import Path

from moses.loop_tui import (
    MosesLoopApp,
    bar,
    breakdown_text,
    current_text,
    diff_text,
    stats_text,
)
from moses.loop_watch import CurrentIteration, read_state


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


def test_stats_text_waiting_when_no_campaign(tmp_path):
    sd = tmp_path / ".moses"
    sd.mkdir()
    s = read_state(sd)
    assert "waiting" in stats_text(s, max_iterations=10).lower()


def test_breakdown_text_lists_weakest(tmp_path):
    s = read_state(_fixture(tmp_path))
    assert "C16" in breakdown_text(s) and "DRY" in breakdown_text(s)


def test_current_text_idle_when_none():
    assert "idle" in current_text(None, "", 0, 0).lower()


def test_current_text_shows_phase_and_target():
    cur = CurrentIteration(iteration=4, max_iterations=10, phase="engine",
                           before_score=84.0, before_violations=61, started_at=1)
    out = current_text(cur, "C14 Shallow nesting", 23, 3)
    assert "4/10" in out and "engine" in out and "C14" in out and "23" in out


def test_breakdown_shows_delta_and_target(tmp_path):
    sd = tmp_path / ".moses"
    campaign = json.loads((_fixture(tmp_path) / "campaign.json").read_text())
    campaign["baseline"]["commandments"] = {"16": 0.0, "12": 100.0}
    verdict = {"commandments": [
        {"number": 16, "name": "DRY", "score_contribution": 10.0, "status": "measured"},
        {"number": 12, "name": "Cog", "score_contribution": 100.0, "status": "measured"},
    ]}
    (sd / "campaign.json").write_text(json.dumps(campaign), encoding="utf-8")
    (sd / "verdict.json").write_text(json.dumps(verdict), encoding="utf-8")
    s = read_state(sd)
    out = breakdown_text(s)
    assert "C16" in out and "C12" in out
    assert "+10.0" in out       # 10.0 now vs 0.0 baseline
    assert "◀" in out           # target marker on the weakest (C16)


def test_diff_text_escapes_markup():
    # git output may contain Rich-markup chars (e.g. a path like foo[bar].py);
    # they must be escaped so rendering can never raise on them.
    out = diff_text("foo[bar].py | 2 +-")
    assert "[b]Last change[/b]" in out
    assert "\\[bar]" in out  # the path's bracket is escaped, not parsed
    assert diff_text("") == ""


async def test_app_mounts_and_renders(tmp_path):
    sd = _fixture(tmp_path)
    app = MosesLoopApp(state_dir=sd, max_iterations=10, process=None)
    async with app.run_test() as pilot:
        await pilot.pause()
        from textual.widgets import Static
        stats = app.query_one("#stats", Static)
        assert "baseline" in str(stats.content)
