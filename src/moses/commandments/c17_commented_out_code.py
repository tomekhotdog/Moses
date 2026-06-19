"""Commandment 17 — No commented-out code.

Runs of ≥2 consecutive `#`-comment lines whose stripped content parses as
Python via ast.parse. Metric: such runs per 1000 LOC. Curve: 100 − 20·M.
"""

from __future__ import annotations

import ast

from ..models import CommandmentResult
from ._ast_helpers import clamp

NUMBER = 17
NAME = "No commented-out code"
MIN_RUN = 2


def _comment_runs(text: str) -> list[tuple[int, str]]:
    """Yield (start_line, joined_code) for runs of ≥2 comment lines that parse.

    A run is a block of consecutive `#`-comment lines. Prose headers often
    precede the dead code (and break a whole-block parse), so within each run we
    look for the largest contiguous sub-block of ≥MIN_RUN lines that parses as
    Python.
    """
    lines = text.splitlines()
    runs = []
    i = 0
    n = len(lines)
    while i < n:
        if lines[i].lstrip().startswith("#"):
            start = i
            block_lines = []
            while i < n and lines[i].lstrip().startswith("#"):
                content = lines[i].lstrip()[1:]
                if content.startswith(" "):
                    content = content[1:]
                block_lines.append(content)
                i += 1
            found = _largest_code_subrun(block_lines)
            if found is not None:
                offset, code = found
                runs.append((start + offset + 1, code))
        else:
            i += 1
    return runs


def _largest_code_subrun(block_lines: list[str]) -> tuple[int, str] | None:
    """Return (offset, code) of the largest contiguous parseable sub-block.

    Tries the widest windows first so a leading prose header is skipped.
    """
    n = len(block_lines)
    for width in range(n, MIN_RUN - 1, -1):
        for offset in range(0, n - width + 1):
            window = block_lines[offset : offset + width]
            code = "\n".join(window)
            if _parses_as_code(code):
                return offset, code
    return None


def _parses_as_code(code: str) -> bool:
    stripped = code.strip()
    if not stripped:
        return False
    # Reject prose: must contain code-ish punctuation.
    if not any(ch in stripped for ch in "=()[].:"):
        return False
    try:
        tree = ast.parse(code)
    except (SyntaxError, ValueError):
        return False
    # An empty module or pure expression of a bare name is likely prose.
    return bool(tree.body)


class NoCommentedOutCode:
    number = NUMBER
    name = NAME

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase) -> CommandmentResult:
        total_loc = 0
        violations = []
        for source in codebase.files:
            total_loc += source.non_blank_loc
            for start, code in _comment_runs(source.text):
                violations.append(
                    {
                        "file": source.relpath,
                        "line": start,
                        "function": "<comment>",
                        "snippet": code.splitlines()[0][:60],
                    }
                )

        if total_loc == 0:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        per_kloc = len(violations) / (total_loc / 1000.0)
        score = clamp(100 - 20 * per_kloc)

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(per_kloc, 2),
            score_contribution=score,
            status="measured",
            detail={"commented_runs": len(violations), "loc": total_loc},
            violations=violations[:50],
        )
