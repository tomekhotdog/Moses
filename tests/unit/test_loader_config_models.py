"""Loader, Config, and model behaviour."""

from __future__ import annotations

from pathlib import Path

from moses.commandments import ALL_COMMANDMENTS
from moses.config import Config, MVP_COMMANDMENTS, WEIGHTS
from moses.loader import load_codebase
from moses.models import SourceFile


def test_weights_sum_to_100():
    assert sum(WEIGHTS.values()) == 100
    assert len(WEIGHTS) == 31


def test_mvp_excludes_unimplemented_via_engine(fixtures_dir):
    # Mutation #20 is in MVP but only runs under --deep.
    assert 20 in MVP_COMMANDMENTS
    cfg = Config()
    assert not cfg.is_enabled(20)
    cfg_deep = Config(deep=True)
    assert cfg_deep.is_enabled(20)


def test_loader_ignores_venv_and_git(tmp_path: Path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "mod.py").write_text("x = 1\n")
    (tmp_path / ".venv").mkdir()
    (tmp_path / ".venv" / "junk.py").write_text("y = 2\n")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "c.py").write_text("z = 3\n")
    cb = load_codebase(tmp_path)
    rels = {f.relpath for f in cb.files}
    assert "pkg/mod.py" in rels
    assert not any(".venv" in r for r in rels)
    assert not any("__pycache__" in r for r in rels)


def test_loader_excludes_glob(tmp_path: Path):
    (tmp_path / "a.py").write_text("a = 1\n")
    (tmp_path / "b_generated.py").write_text("b = 2\n")
    cb = load_codebase(tmp_path, excludes=["*_generated.py"])
    rels = {f.relpath for f in cb.files}
    assert "a.py" in rels
    assert "b_generated.py" not in rels


def test_source_file_is_test_detection(tmp_path: Path):
    f1 = SourceFile(path=tmp_path / "test_foo.py", relpath="test_foo.py", text="")
    f2 = SourceFile(path=tmp_path / "foo.py", relpath="tests/foo.py", text="")
    f3 = SourceFile(path=tmp_path / "bar.py", relpath="src/bar.py", text="")
    assert f1.is_test
    assert f2.is_test
    assert not f3.is_test


def test_config_from_file(tmp_path: Path):
    cfg_file = tmp_path / "moses.yaml"
    cfg_file.write_text("disabled: [11, 13]\nexcludes: ['*.gen.py']\ndeep: true\n")
    cfg = Config.from_file(cfg_file)
    assert not cfg.is_enabled(11)
    assert "*.gen.py" in cfg.excludes
    assert cfg.deep
    assert len(cfg.rule_params) == len(ALL_COMMANDMENTS)
