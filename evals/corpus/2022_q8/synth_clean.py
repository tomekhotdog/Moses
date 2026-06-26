"""Advent of Code 2022, Day 8 — Treetop Tree House.

Counts trees visible from outside the grid (part 1) and finds the maximum
scenic score (part 2).
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from math import prod
from typing import Iterator

# Unit steps for the four cardinal directions, as (drow, dcol).
DIRECTIONS: tuple[tuple[int, int], ...] = (
    (-1, 0),  # up
    (1, 0),   # down
    (0, -1),  # left
    (0, 1),   # right
)


@dataclass(frozen=True)
class Point:
    row: int
    col: int


class Grid:
    """A rectangular grid of single-digit tree heights."""

    def __init__(self, heights: list[list[int]]) -> None:
        self._heights = heights
        self.rows = len(heights)
        self.cols = len(heights[0]) if heights else 0

    @classmethod
    def parse(cls, text: str) -> "Grid":
        heights = [
            [int(char) for char in line]
            for line in text.splitlines()
            if line.strip()
        ]
        return cls(heights)

    def height(self, point: Point) -> int:
        return self._heights[point.row][point.col]

    def contains(self, point: Point) -> bool:
        return 0 <= point.row < self.rows and 0 <= point.col < self.cols

    def points(self) -> Iterator[Point]:
        for row in range(self.rows):
            for col in range(self.cols):
                yield Point(row, col)

    def _ray(self, start: Point, step: tuple[int, int]) -> Iterator[Point]:
        """Yield points outward from `start` (exclusive) until the edge."""
        drow, dcol = step
        current = Point(start.row + drow, start.col + dcol)
        while self.contains(current):
            yield current
            current = Point(current.row + drow, current.col + dcol)

    def is_visible(self, point: Point) -> bool:
        """True if every tree is shorter than `point` along some direction."""
        own_height = self.height(point)
        return any(
            all(self.height(other) < own_height for other in self._ray(point, step))
            for step in DIRECTIONS
        )

    def viewing_distance(self, point: Point, step: tuple[int, int]) -> int:
        own_height = self.height(point)
        distance = 0
        for other in self._ray(point, step):
            distance += 1
            if self.height(other) >= own_height:
                break
        return distance

    def scenic_score(self, point: Point) -> int:
        return prod(self.viewing_distance(point, step) for step in DIRECTIONS)


def count_visible(grid: Grid) -> int:
    return sum(1 for point in grid.points() if grid.is_visible(point))


def best_scenic_score(grid: Grid) -> int:
    return max(grid.scenic_score(point) for point in grid.points())


def main(path: str = "input.txt") -> None:
    grid = Grid.parse(open(path).read())
    print(count_visible(grid))
    print(best_scenic_score(grid))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "input.txt")
