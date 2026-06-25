"""Advent of Code 2024 — Day 6: Guard Gallivant.

A guard walks a grid, turning right whenever an obstacle is directly ahead,
until it leaves the map. Part 1 counts distinct visited cells; Part 2 counts
single obstruction placements that would trap the guard in a loop.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

OBSTACLE = "#"
GUARD_START = "^"


@dataclass(frozen=True)
class Direction:
    """A unit step on the grid, with right-hand rotation."""

    row: int
    col: int

    def turn_right(self) -> "Direction":
        # (row, col) rotated 90° clockwise: up -> right -> down -> left.
        return Direction(row=self.col, col=-self.row)


UP = Direction(row=-1, col=0)


@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def step(self, direction: Direction) -> "Position":
        return Position(row=self.row + direction.row, col=self.col + direction.col)


class Grid:
    """An immutable lab map plus optional extra obstruction for what-if runs."""

    def __init__(self, obstacles: frozenset[Position], height: int, width: int, start: Position):
        self._obstacles = obstacles
        self.height = height
        self.width = width
        self.start = start

    @classmethod
    def parse(cls, text: str) -> "Grid":
        obstacles: set[Position] = set()
        start: Position | None = None
        rows = [line for line in text.splitlines() if line]
        for r, line in enumerate(rows):
            for c, char in enumerate(line):
                if char == OBSTACLE:
                    obstacles.add(Position(r, c))
                elif char == GUARD_START:
                    start = Position(r, c)
        if start is None:
            raise ValueError("no guard start found in grid")
        return cls(frozenset(obstacles), len(rows), len(rows[0]), start)

    def contains(self, pos: Position) -> bool:
        return 0 <= pos.row < self.height and 0 <= pos.col < self.width

    def is_obstacle(self, pos: Position, extra: Position | None = None) -> bool:
        return pos in self._obstacles or pos == extra

    def open_cells(self) -> frozenset[Position]:
        all_cells = {
            Position(r, c) for r in range(self.height) for c in range(self.width)
        }
        return frozenset(all_cells - self._obstacles)


def walk(grid: Grid, extra_obstacle: Position | None = None) -> tuple[set[Position], bool]:
    """Simulate the patrol.

    Returns the set of visited positions and whether the guard entered a loop.
    """
    pos, direction = grid.start, UP
    seen_states: set[tuple[Position, Direction]] = set()
    visited: set[Position] = set()

    while grid.contains(pos):
        if (pos, direction) in seen_states:
            return visited, True
        seen_states.add((pos, direction))
        visited.add(pos)

        ahead = pos.step(direction)
        if grid.is_obstacle(ahead, extra_obstacle):
            direction = direction.turn_right()
        else:
            pos = ahead

    return visited, False


def part1(grid: Grid) -> int:
    visited, _ = walk(grid)
    return len(visited)


def part2(grid: Grid) -> int:
    patrol_path, _ = walk(grid)
    candidates = patrol_path - {grid.start}
    return sum(walk(grid, extra_obstacle=cell)[1] for cell in candidates)


def main() -> None:
    text = open(sys.argv[1]).read()
    grid = Grid.parse(text)
    print(part1(grid))
    print(part2(grid))


if __name__ == "__main__":
    main()
