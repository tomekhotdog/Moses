"""Commandment 16 — DRY.

Token-level near-duplicate detection across files. Built-in tokeniser by
default (min block ≥ 50 tokens), or shell out to jscpd if jscpd_path is set.
Metric: duplicated-token fraction. Curve: 100 − 1000·M (0 at ≥ 10%).
"""

from __future__ import annotations

import io
import keyword
import tokenize
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp

NUMBER = 16
NAME = "DRY"


@dataclass(frozen=True)
class RuleConfig:
    min_block_tokens: int = 50
    slope: float = 1000.0


def _tokenise(text: str) -> list[tuple[str, str, int]]:
    """Return [(type_name, normalised_value, line)]; skip trivia.

    Names and literals are normalised to placeholders so structurally identical
    blocks with different identifiers still count as duplicates.
    """
    out = []
    try:
        tokens = tokenize.generate_tokens(io.StringIO(text).readline)
        for tok in tokens:
            if tok.type in (
                tokenize.ENCODING,
                tokenize.NL,
                tokenize.NEWLINE,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.COMMENT,
                tokenize.ENDMARKER,
            ):
                continue
            if tok.type == tokenize.STRING:
                value = "STR"
            elif tok.type == tokenize.NUMBER:
                value = "NUM"
            elif tok.type == tokenize.NAME:
                value = "NAME" if not _is_keyword(tok.string) else tok.string
            else:
                value = tok.string
            out.append((tokenize.tok_name[tok.type], value, tok.start[0]))
    except (tokenize.TokenError, IndentationError):
        pass
    return out


def _is_keyword(s: str) -> bool:
    return keyword.iskeyword(s)


def _duplicate_fraction(per_file_tokens: dict[str, list[tuple[str, str, int]]], min_block_tokens: int):
    """Hash sliding windows of min_block_tokens; count tokens in repeated windows."""
    window = min_block_tokens
    seen: dict[int, tuple[str, int]] = {}
    duplicated_lines: dict[str, set[int]] = {}
    total_tokens = 0

    # Flatten and index per file.
    flat: list[tuple[str, str, int]] = []
    file_spans: list[tuple[str, int, int]] = []
    for relpath, toks in per_file_tokens.items():
        start = len(flat)
        flat.extend(toks)
        file_spans.append((relpath, start, len(flat)))
        total_tokens += len(toks)

    if total_tokens == 0:
        return 0.0, {}

    values = [t[1] for t in flat]

    def file_of(idx: int) -> tuple[str, int]:
        for relpath, s, e in file_spans:
            if s <= idx < e:
                return relpath, flat[idx][2]
        return "?", 0

    duplicated_token_indices: set[int] = set()
    for i in range(0, len(values) - window + 1):
        h = hash(tuple(values[i : i + window]))
        if h in seen:
            for j in range(i, i + window):
                duplicated_token_indices.add(j)
            prev_start = seen[h][1]
            for j in range(prev_start, prev_start + window):
                duplicated_token_indices.add(j)
        else:
            seen[h] = ("", i)

    for idx in duplicated_token_indices:
        relpath, line = file_of(idx)
        duplicated_lines.setdefault(relpath, set()).add(line)

    fraction = len(duplicated_token_indices) / total_tokens
    return fraction, duplicated_lines


class DRY:
    number = NUMBER
    name = NAME
    RuleConfig = RuleConfig

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult:
        per_file = {}
        for source in codebase.files:
            toks = _tokenise(source.text)
            if toks:
                per_file[source.relpath] = toks

        if not per_file:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        fraction, dup_lines = _duplicate_fraction(per_file, config.min_block_tokens)
        score = clamp(100 - config.slope * fraction)

        violations = []
        for relpath, lines in dup_lines.items():
            for line in sorted(lines)[:10]:
                violations.append(
                    {
                        "file": relpath,
                        "line": line,
                        "function": "<duplicate-block>",
                    }
                )

        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(fraction, 4),
            score_contribution=score,
            status="measured",
            detail={"duplicate_fraction": round(fraction, 4)},
            violations=violations[:50],
        )
