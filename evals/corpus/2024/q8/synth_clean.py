"""AoC 2024 Day 8: Resonant Collinearity.

Counts antinode positions produced by collinear pairs of same-frequency antennas.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations
from typing import Iterator


EMPTY = "."


@dataclass(frozen=True)
class Point:
    """A grid coordinate. Supports vector arithmetic between points."""

    row: int
    col: int

    def __add__(self, other: "Point") -> "Point":
        return Point(self.row + other.row, self.col + other.col)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.row - other.row, self.col - other.col)


@dataclass(frozen=True)
class Grid:
    """A rectangular map of antennas indexed by frequency."""

    height: int
    width: int
    antennas_by_frequency: dict[str, list[Point]]

    @classmethod
    def parse(cls, text: str) -> "Grid":
        lines = [line for line in text.splitlines() if line]
        antennas: dict[str, list[Point]] = defaultdict(list)
        for row, line in enumerate(lines):
            for col, char in enumerate(line):
                if char != EMPTY:
                    antennas[char].append(Point(row, col))
        return cls(len(lines), len(lines[0]), dict(antennas))

    def contains(self, point: Point) -> bool:
        return 0 <= point.row < self.height and 0 <= point.col < self.width

    def antenna_pairs(self) -> Iterator[tuple[Point, Point]]:
        """Yield every unordered pair of antennas sharing a frequency."""
        for points in self.antennas_by_frequency.values():
            yield from combinations(points, 2)


def simple_antinodes(grid: Grid, a: Point, b: Point) -> Iterator[Point]:
    """The two reflections where one antenna is twice as far as the other."""
    offset = b - a
    for candidate in (b + offset, a - offset):
        if grid.contains(candidate):
            yield candidate


def resonant_antinodes(grid: Grid, a: Point, b: Point) -> Iterator[Point]:
    """Every in-bounds grid point collinear with the pair, both directions."""
    offset = b - a
    for start, step in ((a, Point(-offset.row, -offset.col)), (b, offset)):
        current = start
        while grid.contains(current):
            yield current
            current = current + step


def count_antinodes(grid: Grid, resonant: bool) -> int:
    generator = resonant_antinodes if resonant else simple_antinodes
    antinodes: set[Point] = set()
    for a, b in grid.antenna_pairs():
        antinodes.update(generator(grid, a, b))
    return len(antinodes)


def part1(grid: Grid) -> int:
    return count_antinodes(grid, resonant=False)


def part2(grid: Grid) -> int:
    return count_antinodes(grid, resonant=True)


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "q8.txt"
    with open(path) as handle:
        grid = Grid.parse(handle.read())
    print(part1(grid))
    print(part2(grid))


if __name__ == "__main__":
    main()
