"""Advent of Code 2023, Day 11 — Cosmic Expansion.

Sum of pairwise Manhattan distances between galaxies in a universe where empty
rows and columns are expanded by a configurable factor.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from itertools import combinations
from typing import Iterator

GALAXY = "#"
PART1_EXPANSION = 2
PART2_EXPANSION = 1_000_000


@dataclass(frozen=True)
class Point:
    """A position on the (possibly expanded) galaxy grid."""

    row: int
    col: int

    def manhattan_to(self, other: "Point") -> int:
        return abs(self.row - other.row) + abs(self.col - other.col)


@dataclass(frozen=True)
class Universe:
    """A parsed star chart: galaxy positions plus the empty rows and columns."""

    galaxies: tuple[Point, ...]
    empty_rows: frozenset[int]
    empty_cols: frozenset[int]

    @classmethod
    def parse(cls, text: str) -> "Universe":
        rows = [line for line in text.splitlines() if line]
        width = len(rows[0])

        galaxies = tuple(
            Point(r, c)
            for r, line in enumerate(rows)
            for c, char in enumerate(line)
            if char == GALAXY
        )

        occupied_rows = {p.row for p in galaxies}
        occupied_cols = {p.col for p in galaxies}
        empty_rows = frozenset(r for r in range(len(rows)) if r not in occupied_rows)
        empty_cols = frozenset(c for c in range(width) if c not in occupied_cols)

        return cls(galaxies, empty_rows, empty_cols)

    def expanded(self, factor: int) -> "Universe":
        """Return a new Universe with empty rows/cols scaled by ``factor``.

        Each empty line is replaced by ``factor`` lines, so coordinates beyond it
        shift by ``factor - 1`` per crossed empty line.
        """
        added = factor - 1
        moved = tuple(
            Point(
                point.row + added * sum(1 for r in self.empty_rows if r < point.row),
                point.col + added * sum(1 for c in self.empty_cols if c < point.col),
            )
            for point in self.galaxies
        )
        return Universe(moved, frozenset(), frozenset())

    def pairwise_distances(self) -> Iterator[int]:
        for a, b in combinations(self.galaxies, 2):
            yield a.manhattan_to(b)


def sum_of_distances(universe: Universe, expansion_factor: int) -> int:
    return sum(universe.expanded(expansion_factor).pairwise_distances())


def main(path: str) -> None:
    with open(path) as handle:
        universe = Universe.parse(handle.read())

    print("Part 1:", sum_of_distances(universe, PART1_EXPANSION))
    print("Part 2:", sum_of_distances(universe, PART2_EXPANSION))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "input.txt")
