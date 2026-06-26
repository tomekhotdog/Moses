"""AoC 2023 Day 1 — Trebuchet?!

Sums per-line calibration values, where a value is the first and last digit of a
line concatenated. In part two, spelled-out number words also count as digits,
including overlapping occurrences such as "twone".
"""

from __future__ import annotations

WORD_TO_DIGIT: dict[str, int] = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
}


def _digit_at(text: str, index: int, include_words: bool) -> int | None:
    """Return the digit beginning at ``index``, or ``None`` if none starts there.

    A single ASCII digit always counts. When ``include_words`` is set, a
    spelled-out number word also counts. Matching anchors at ``index`` and never
    consumes following characters, so overlapping words remain detectable on the
    next position.
    """
    char = text[index]
    if char.isdigit():
        return int(char)
    if include_words:
        for word, value in WORD_TO_DIGIT.items():
            if text.startswith(word, index):
                return value
    return None


def _digits(text: str, include_words: bool) -> list[int]:
    """Return every digit in ``text`` in left-to-right order."""
    return [
        digit
        for index in range(len(text))
        if (digit := _digit_at(text, index, include_words)) is not None
    ]


def calibration_value(line: str, include_words: bool) -> int:
    """Combine the first and last digit of ``line`` into a two-digit number."""
    digits = _digits(line, include_words)
    if not digits:
        raise ValueError(f"line contains no digits: {line!r}")
    return digits[0] * 10 + digits[-1]


def solve(lines: list[str], include_words: bool) -> int:
    """Sum the calibration values of every non-empty line."""
    return sum(calibration_value(line, include_words) for line in lines if line)


def part_one(lines: list[str]) -> int:
    return solve(lines, include_words=False)


def part_two(lines: list[str]) -> int:
    return solve(lines, include_words=True)
