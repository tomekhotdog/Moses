"""Advent of Code 2024 Day 15 — Warehouse Woes.

A robot pushes boxes around a walled grid. Part 1 uses single-cell boxes;
Part 2 doubles the warehouse width so boxes span two cells and vertical
pushes can fan out across a connected group.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

# A position is (row, col); a direction is a (drow, dcol) unit step.
Position = tuple[int, int]
Direction = tuple[int, int]

WALL = "#"
EMPTY = "."
ROBOT = "@"
BOX = "O"
BOX_LEFT = "["
BOX_RIGHT = "]"

GPS_ROW_WEIGHT = 100

DIRECTIONS: dict[str, Direction] = {
    "^": (-1, 0),
    "v": (1, 0),
    "<": (0, -1),
    ">": (0, 1),
}

# How a single tile of the narrow warehouse expands into the wide warehouse.
WIDENING: dict[str, str] = {
    WALL: WALL + WALL,
    BOX: BOX_LEFT + BOX_RIGHT,
    EMPTY: EMPTY + EMPTY,
    ROBOT: ROBOT + EMPTY,
}


def step(position: Position, direction: Direction) -> Position:
    return position[0] + direction[0], position[1] + direction[1]


@dataclass
class Warehouse:
    """A mutable grid of tiles plus the robot's current position."""

    grid: list[list[str]]
    robot: Position

    @classmethod
    def from_lines(cls, lines: list[str], *, widen: bool) -> "Warehouse":
        rows: list[list[str]] = []
        for line in lines:
            rendered = "".join(WIDENING[tile] for tile in line) if widen else line
            rows.append(list(rendered))
        robot = cls._locate_robot(rows)
        rows[robot[0]][robot[1]] = EMPTY
        return cls(rows, robot)

    @staticmethod
    def _locate_robot(rows: list[list[str]]) -> Position:
        for r, row in enumerate(rows):
            for c, tile in enumerate(row):
                if tile == ROBOT:
                    return (r, c)
        raise ValueError("no robot in grid")

    def tile(self, position: Position) -> str:
        return self.grid[position[0]][position[1]]

    def run(self, moves: str) -> None:
        for symbol in moves:
            self._try_move(DIRECTIONS[symbol])

    def gps_total(self) -> int:
        return sum(
            GPS_ROW_WEIGHT * r + c
            for r, row in enumerate(self.grid)
            for c, tile in enumerate(row)
            if tile in (BOX, BOX_LEFT)
        )

    def _try_move(self, direction: Direction) -> None:
        ahead = step(self.robot, direction)
        cluster = self._pushable_cluster(ahead, direction)
        if cluster is None:
            return
        self._shift(cluster, direction)
        self.robot = ahead

    def _pushable_cluster(
        self, start: Position, direction: Direction
    ) -> set[Position] | None:
        """Return every box cell that must move, or None if the move is blocked.

        Explores the connected group of box cells the robot would push. A wide
        box dragged vertically pulls its partner cell along, so both halves are
        always added together.
        """
        cluster: set[Position] = set()
        frontier = [start]
        while frontier:
            cell = frontier.pop()
            tile = self.tile(cell)
            if tile == WALL:
                return None
            if tile == EMPTY or cell in cluster:
                continue
            partner = self._box_partner(cell, tile, direction)
            for occupied in (cell, partner):
                if occupied is not None and occupied not in cluster:
                    cluster.add(occupied)
                    frontier.append(step(occupied, direction))
        return cluster

    @staticmethod
    def _box_partner(
        cell: Position, tile: str, direction: Direction
    ) -> Position | None:
        """The other half of a wide box, only relevant for vertical pushes."""
        is_vertical = direction[1] == 0
        if not is_vertical:
            return None
        if tile == BOX_LEFT:
            return (cell[0], cell[1] + 1)
        if tile == BOX_RIGHT:
            return (cell[0], cell[1] - 1)
        return None

    def _shift(self, cluster: set[Position], direction: Direction) -> None:
        contents = {cell: self.tile(cell) for cell in cluster}
        for cell in cluster:
            self.grid[cell[0]][cell[1]] = EMPTY
        for cell, tile in contents.items():
            destination = step(cell, direction)
            self.grid[destination[0]][destination[1]] = tile


def parse(text: str) -> tuple[list[str], str]:
    grid_block, move_block = text.split("\n\n")
    return grid_block.splitlines(), move_block.replace("\n", "")


def solve(lines: list[str], moves: str, *, widen: bool) -> int:
    warehouse = Warehouse.from_lines(lines, widen=widen)
    warehouse.run(moves)
    return warehouse.gps_total()


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    lines, moves = parse(open(path).read())
    print(solve(lines, moves, widen=False))
    print(solve(lines, moves, widen=True))


if __name__ == "__main__":
    main()
