"""Advent of Code 2024, Day 4: Ceres Search."""
from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

WORD = "XMAS"


class Point(NamedTuple):
    row: int
    col: int

    def step(self, direction: "Point", times: int = 1) -> "Point":
        return Point(self.row + direction.row * times, self.col + direction.col * times)


# Eight compass directions as unit (row, col) offsets.
DIRECTIONS: tuple[Point, ...] = tuple(
    Point(dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if not (dr == 0 and dc == 0)
)

# The two diagonal pairs that form an X around a center cell.
MAIN_DIAGONAL = (Point(-1, -1), Point(1, 1))
ANTI_DIAGONAL = (Point(-1, 1), Point(1, -1))


class Grid:
    def __init__(self, rows: list[str]) -> None:
        self._rows = rows
        self.height = len(rows)
        self.width = len(rows[0]) if rows else 0

    @classmethod
    def from_file(cls, path: Path) -> "Grid":
        return cls(path.read_text().splitlines())

    def contains(self, point: Point) -> bool:
        return 0 <= point.row < self.height and 0 <= point.col < self.width

    def at(self, point: Point) -> str:
        return self._rows[point.row][point.col]

    def points(self):
        for row in range(self.height):
            for col in range(self.width):
                yield Point(row, col)


def spells_word(grid: Grid, start: Point, direction: Point, word: str) -> bool:
    cells = [start.step(direction, i) for i in range(len(word))]
    if not all(grid.contains(cell) for cell in cells):
        return False
    return "".join(grid.at(cell) for cell in cells) == word


def count_xmas(grid: Grid) -> int:
    return sum(
        spells_word(grid, point, direction, WORD)
        for point in grid.points()
        for direction in DIRECTIONS
    )


def is_mas_pair(grid: Grid, center: Point, diagonal: tuple[Point, Point]) -> bool:
    ends = [center.step(offset) for offset in diagonal]
    if not all(grid.contains(end) for end in ends):
        return False
    return {grid.at(ends[0]), grid.at(ends[1])} == {"M", "S"}


def count_x_mas(grid: Grid) -> int:
    return sum(
        grid.at(center) == "A"
        and is_mas_pair(grid, center, MAIN_DIAGONAL)
        and is_mas_pair(grid, center, ANTI_DIAGONAL)
        for center in grid.points()
    )


def main() -> None:
    grid = Grid.from_file(Path("input.txt"))
    print("Part 1:", count_xmas(grid))
    print("Part 2:", count_x_mas(grid))


if __name__ == "__main__":
    main()
