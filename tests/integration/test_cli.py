"""CLI integration: judge, prompt, version, JSON/HTML output, exit codes."""

from __future__ import annotations

import json

from click.testing import CliRunner

from moses.cli import main


def test_version():
    result = CliRunner().invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


def test_judge_good_exits_zero(fixtures_dir):
    result = CliRunner().invoke(main, ["judge", str(fixtures_dir / "good_example"), "--quiet"])
    # Good fixture earns an A/B/C → exit 0.
    assert result.exit_code == 0


def test_judge_writes_json(tmp_path, fixtures_dir):
    out = tmp_path / "verdict.json"
    result = CliRunner().invoke(
        main,
        ["judge", str(fixtures_dir / "bad_example"), "--quiet", "--json", str(out)],
    )
    assert result.exit_code in (0, 1, 2)
    data = json.loads(out.read_text())
    assert data["schema_version"] == 1
    assert 0 <= data["score"] <= 100
    assert data["grade"] in {"A", "B", "C", "D", "E", "F"}
    assert any(c["number"] == 3 for c in data["commandments"])


def test_judge_writes_html(tmp_path, fixtures_dir):
    out = tmp_path / "report.html"
    CliRunner().invoke(
        main,
        ["judge", str(fixtures_dir / "bad_example"), "--quiet", "--html", str(out)],
    )
    html = out.read_text()
    assert "<html" in html.lower()
    assert "Score" in html


def test_judge_disable_changes_score(tmp_path, fixtures_dir):
    base = tmp_path / "a.json"
    disabled = tmp_path / "b.json"
    CliRunner().invoke(main, ["judge", str(fixtures_dir / "bad_example"), "--quiet", "--json", str(base)])
    CliRunner().invoke(
        main,
        ["judge", str(fixtures_dir / "bad_example"), "--quiet", "--disable", "16", "--json", str(disabled)],
    )
    a = json.loads(base.read_text())["score"]
    b = json.loads(disabled.read_text())["score"]
    # Disabling a failing rule must move the Score (and not by padding 100s).
    assert a != b


def test_prompt_renders_brief():
    result = CliRunner().invoke(main, ["prompt", "3"])
    assert result.exit_code == 0
    assert "pass-through" in result.output.lower()


def test_prompt_unknown_falls_back():
    result = CliRunner().invoke(main, ["prompt", "9"])
    assert result.exit_code == 0
    assert "Commandment 9" in result.output
