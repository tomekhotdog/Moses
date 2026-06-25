"""AoC 2024 Day 12 - Garden Groups.

Part 1: sum of area * perimeter over all regions.
Part 2: sum of area * number of sides (== number of corners) over all regions.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Iterator, NamedTuple

ORTHOGONAL = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIAGONAL = ((-1, -1), (-1, 1), (1, -1), (1, 1))


class Point(NamedTuple):
    row: int
    col: int

    def neighbours(self) -> Iterator["Point"]:
        for d_row, d_col in ORTHOGONAL:
            yield Point(self.row + d_row, self.col + d_col)


@dataclass(frozen=True)
class Grid:
    rows: tuple[str, ...]

    @classmethod
    def parse(cls, text: str) -> "Grid":
        lines = [line for line in text.splitlines() if line.strip()]
        return cls(tuple(lines))

    @property
    def height(self) -> int:
        return len(self.rows)

    @property
    def width(self) -> int:
        return len(self.rows[0])

    def plant_at(self, point: Point) -> str | None:
        if 0 <= point.row < self.height and 0 <= point.col < self.width:
            return self.rows[point.row][point.col]
        return None

    def points(self) -> Iterator[Point]:
        for row in range(self.height):
            for col in range(self.width):
                yield Point(row, col)


@dataclass(frozen=True)
class Region:
    plant: str
    cells: frozenset[Point]

    @property
    def area(self) -> int:
        return len(self.cells)

    @property
    def perimeter(self) -> int:
        exposed_edges = 0
        for cell in self.cells:
            for neighbour in cell.neighbours():
                if neighbour not in self.cells:
                    exposed_edges += 1
        return exposed_edges

    @property
    def corners(self) -> int:
        """Number of straight fence sides equals the number of corners."""
        total = 0
        for cell in self.cells:
            total += self._corners_at(cell)
        return total

    def _corners_at(self, cell: Point) -> int:
        count = 0
        for d_row, d_col in DIAGONAL:
            vertical_inside = Point(cell.row + d_row, cell.col) in self.cells
            horizontal_inside = Point(cell.row, cell.col + d_col) in self.cells
            diagonal_inside = Point(cell.row + d_row, cell.col + d_col) in self.cells
            is_convex = not vertical_inside and not horizontal_inside
            is_concave = vertical_inside and horizontal_inside and not diagonal_inside
            if is_convex or is_concave:
                count += 1
        return count

    @property
    def fence_price(self) -> int:
        return self.area * self.perimeter

    @property
    def bulk_price(self) -> int:
        return self.area * self.corners


def find_regions(grid: Grid) -> list[Region]:
    visited: set[Point] = set()
    regions: list[Region] = []
    for start in grid.points():
        if start in visited:
            continue
        plant = grid.plant_at(start)
        cells = _flood_fill(grid, start, plant)
        visited |= cells
        regions.append(Region(plant, frozenset(cells)))
    return regions


def _flood_fill(grid: Grid, start: Point, plant: str | None) -> set[Point]:
    region: set[Point] = set()
    stack = [start]
    while stack:
        cell = stack.pop()
        if cell in region:
            continue
        region.add(cell)
        for neighbour in cell.neighbours():
            if neighbour not in region and grid.plant_at(neighbour) == plant:
                stack.append(neighbour)
    return region


def part1(grid: Grid) -> int:
    return sum(region.fence_price for region in find_regions(grid))


def part2(grid: Grid) -> int:
    return sum(region.bulk_price for region in find_regions(grid))


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "example3.txt"
    with open(path, encoding="utf-8") as handle:
        grid = Grid.parse(handle.read())
    print(part1(grid))
    print(part2(grid))


if __name__ == "__main__":
    main()
