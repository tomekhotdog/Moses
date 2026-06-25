"""Advent of Code 2024 Day 10: Hoof It.

Counts hiking-trail scores (Part 1) and ratings (Part 2) on a
topographic height map. A trail ascends from height 0 to height 9,
increasing by exactly one at each orthogonal step.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator

Position = tuple[int, int]

TRAILHEAD_HEIGHT = 0
SUMMIT_HEIGHT = 9
STEP = 1
DIRECTIONS: tuple[Position, ...] = ((1, 0), (-1, 0), (0, 1), (0, -1))


class TopographicMap:
    """A grid of integer heights supporting trail traversal."""

    def __init__(self, heights: list[list[int]]) -> None:
        self._heights = heights
        self._rows = len(heights)
        self._cols = len(heights[0]) if heights else 0

    @classmethod
    def parse(cls, text: str) -> "TopographicMap":
        heights = [
            [int(char) for char in line]
            for line in text.splitlines()
            if line
        ]
        return cls(heights)

    def height_at(self, position: Position) -> int:
        row, col = position
        return self._heights[row][col]

    def contains(self, position: Position) -> bool:
        row, col = position
        return 0 <= row < self._rows and 0 <= col < self._cols

    def trailheads(self) -> Iterator[Position]:
        for row in range(self._rows):
            for col in range(self._cols):
                if self._heights[row][col] == TRAILHEAD_HEIGHT:
                    yield (row, col)

    def uphill_neighbours(self, position: Position) -> Iterator[Position]:
        row, col = position
        target = self.height_at(position) + STEP
        for delta_row, delta_col in DIRECTIONS:
            neighbour = (row + delta_row, col + delta_col)
            if self.contains(neighbour) and self.height_at(neighbour) == target:
                yield neighbour


def reachable_summits(grid: TopographicMap, trailhead: Position) -> set[Position]:
    """Return the distinct summit cells reachable from a trailhead."""
    summits: set[Position] = set()
    stack = [trailhead]
    while stack:
        position = stack.pop()
        if grid.height_at(position) == SUMMIT_HEIGHT:
            summits.add(position)
            continue
        stack.extend(grid.uphill_neighbours(position))
    return summits


def count_distinct_trails(grid: TopographicMap, trailhead: Position) -> int:
    """Count distinct ascending paths from a trailhead to any summit."""
    if grid.height_at(trailhead) == SUMMIT_HEIGHT:
        return 1
    return sum(
        count_distinct_trails(grid, neighbour)
        for neighbour in grid.uphill_neighbours(trailhead)
    )


def part_one(grid: TopographicMap) -> int:
    return sum(len(reachable_summits(grid, head)) for head in grid.trailheads())


def part_two(grid: TopographicMap) -> int:
    return sum(count_distinct_trails(grid, head) for head in grid.trailheads())


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "q10.txt"
    with open(path, encoding="utf-8") as handle:
        grid = TopographicMap.parse(handle.read())
    print(part_one(grid))
    print(part_two(grid))


if __name__ == "__main__":
    main()
