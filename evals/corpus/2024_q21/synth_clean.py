"""AoC 2024 Day 21 - Keypad Conundrum.

Computes the sum of code complexities for a chain of directional keypads.
Part 1 uses 2 intermediate directional keypads, Part 2 uses 25. The cost of a
keypad chain is found by memoized recursion over (button-pair, depth), tracking
sequence lengths only.
"""

from __future__ import annotations

import sys
from functools import cache
from itertools import pairwise
from typing import Iterable

Position = tuple[int, int]
KeypadLayout = dict[str, Position]

NUMERIC_KEYPAD: KeypadLayout = {
    "7": (0, 0), "8": (1, 0), "9": (2, 0),
    "4": (0, 1), "5": (1, 1), "6": (2, 1),
    "1": (0, 2), "2": (1, 2), "3": (2, 2),
    "0": (1, 3), "A": (2, 3),
}
NUMERIC_GAP: Position = (0, 3)

DIRECTIONAL_KEYPAD: KeypadLayout = {
    "^": (1, 0), "A": (2, 0),
    "<": (0, 1), "v": (1, 1), ">": (2, 1),
}
DIRECTIONAL_GAP: Position = (0, 0)


def paths_between(start: Position, end: Position, gap: Position) -> list[str]:
    """All shortest directional sequences from start to end that avoid the gap.

    A shortest path groups all horizontal moves and all vertical moves; only
    the two orderings (horizontal-first, vertical-first) can be optimal. Each
    returned sequence ends with 'A' to press the target button.
    """
    sx, sy = start
    ex, ey = end
    horizontal = (">" if ex > sx else "<") * abs(ex - sx)
    vertical = ("v" if ey > sy else "^") * abs(ey - sy)

    candidates = []
    if (ex, sy) != gap:  # horizontal first: travels along start row to end column
        candidates.append(horizontal + vertical + "A")
    if (sx, ey) != gap:  # vertical first: travels along start column to end row
        candidates.append(vertical + horizontal + "A")
    return list(dict.fromkeys(candidates))  # dedupe (pure horizontal/vertical)


@cache
def sequence_cost(transition: str, depth: int) -> int:
    """Min outermost presses to execute one button transition at `depth` pads.

    `transition` is a two-character pair (from, to) on a directional keypad.
    At depth 0 the human presses directly, so one move costs one press.
    """
    if depth == 0:
        return 1
    start, end = DIRECTIONAL_KEYPAD[transition[0]], DIRECTIONAL_KEYPAD[transition[1]]
    return min(
        cheapest_to_type(path, depth - 1)
        for path in paths_between(start, end, DIRECTIONAL_GAP)
    )


def cheapest_to_type(sequence: str, depth: int) -> int:
    """Min presses to type `sequence` on a directional pad at the given depth."""
    primed = "A" + sequence
    return sum(sequence_cost(a + b, depth) for a, b in pairwise(primed))


def code_length(code: str, directional_pads: int) -> int:
    """Shortest outermost sequence length to enter a numeric `code`."""
    primed = "A" + code
    total = 0
    for from_key, to_key in pairwise(primed):
        start, end = NUMERIC_KEYPAD[from_key], NUMERIC_KEYPAD[to_key]
        total += min(
            cheapest_to_type(path, directional_pads)
            for path in paths_between(start, end, NUMERIC_GAP)
        )
    return total


def numeric_part(code: str) -> int:
    return int("".join(ch for ch in code if ch.isdigit()))


def total_complexity(codes: Iterable[str], directional_pads: int) -> int:
    return sum(code_length(c, directional_pads) * numeric_part(c) for c in codes)


def read_codes(path: str) -> list[str]:
    with open(path) as handle:
        return [line.strip() for line in handle if line.strip()]


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
    codes = read_codes(path)
    print("Part 1:", total_complexity(codes, directional_pads=2))
    print("Part 2:", total_complexity(codes, directional_pads=25))


if __name__ == "__main__":
    main()
