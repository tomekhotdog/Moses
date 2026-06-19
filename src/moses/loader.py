"""Walks a source tree and loads Python files into a Codebase."""

from __future__ import annotations

import fnmatch
from pathlib import Path

from .models import Codebase, SourceFile

DEFAULT_IGNORE_DIRS = {
    ".venv",
    "venv",
    ".git",
    "build",
    "dist",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".tox",
    "node_modules",
    ".eggs",
    ".moses",
    "site-packages",
}


def _is_ignored_dir(name: str) -> bool:
    if name in DEFAULT_IGNORE_DIRS:
        return True
    return name.endswith(".egg-info")


def _matches_exclude(relpath: str, excludes: list[str]) -> bool:
    for pattern in excludes:
        if fnmatch.fnmatch(relpath, pattern) or fnmatch.fnmatch(Path(relpath).name, pattern):
            return True
        # Also match if any path segment matches a directory-style glob.
        if fnmatch.fnmatch(relpath, pattern.rstrip("/") + "/*"):
            return True
    return False


def load_codebase(root: str | Path, excludes: list[str] | None = None) -> Codebase:
    """Load all non-ignored ``*.py`` files under ``root`` into a Codebase."""
    root_path = Path(root).resolve()
    excludes = excludes or []
    files: list[SourceFile] = []

    if root_path.is_file():
        candidates = [root_path]
        base = root_path.parent
    else:
        candidates = []
        base = root_path
        for path in sorted(root_path.rglob("*.py")):
            parts = path.relative_to(root_path).parts
            if any(_is_ignored_dir(p) for p in parts[:-1]):
                continue
            candidates.append(path)

    for path in candidates:
        if path.suffix != ".py":
            continue
        try:
            relpath = str(path.relative_to(base))
        except ValueError:
            relpath = path.name
        if _matches_exclude(relpath, excludes):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        files.append(SourceFile(path=path, relpath=relpath, text=text))

    return Codebase(root=root_path, files=files)
