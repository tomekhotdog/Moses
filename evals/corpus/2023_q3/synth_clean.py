"""Advent of Code 2023, Day 3 - Gear Ratios.

A clean, typed solution built around small abstractions:

* ``Position``    - a single (row, column) cell.
* ``Number``      - a multi-digit number with the cells it occupies.
* ``Schematic``   - the parsed grid, exposing the queries each part needs.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from functools import cached_property
from math import prod


# Relative offsets of the eight cells surrounding any cell.
NEIGHBOUR_OFFSETS: tuple[tuple[int, int], ...] = tuple(
    (dr, dc)
    for dr in (-1, 0, 1)
    for dc in (-1, 0, 1)
    if (dr, dc) != (0, 0)
)


@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def neighbours(self) -> frozenset["Position"]:
        return frozenset(
            Position(self.row + dr, self.col + dc)
            for dr, dc in NEIGHBOUR_OFFSETS
        )


@dataclass(frozen=True)
class Number:
    value: int
    cells: frozenset[Position]

    @cached_property
    def neighbourhood(self) -> frozenset[Position]:
        """All cells adjacent to the number, excluding its own cells."""
        surrounding: set[Position] = set()
        for cell in self.cells:
            surrounding |= cell.neighbours()
        return frozenset(surrounding) - self.cells

    def touches(self, position: Position) -> bool:
        return position in self.neighbourhood


def _is_symbol(char: str) -> bool:
    return char != "." and not char.isdigit()


@dataclass
class Schematic:
    numbers: list[Number]
    symbols: dict[Position, str]

    @classmethod
    def parse(cls, text: str) -> "Schematic":
        numbers: list[Number] = []
        symbols: dict[Position, str] = {}

        for row, line in enumerate(text.splitlines()):
            col = 0
            while col < len(line):
                char = line[col]
                if char.isdigit():
                    start = col
                    while col < len(line) and line[col].isdigit():
                        col += 1
                    cells = frozenset(
                        Position(row, c) for c in range(start, col)
                    )
                    numbers.append(Number(int(line[start:col]), cells))
                    continue
                if _is_symbol(char):
                    symbols[Position(row, col)] = char
                col += 1

        return cls(numbers, symbols)

    @property
    def part_numbers(self) -> list[Number]:
        return [
            number
            for number in self.numbers
            if any(self.symbols.keys() & number.neighbourhood)
        ]

    @property
    def gear_ratios(self) -> list[int]:
        ratios: list[int] = []
        for position, char in self.symbols.items():
            if char != "*":
                continue
            adjacent = [n for n in self.numbers if n.touches(position)]
            if len(adjacent) == 2:
                ratios.append(prod(n.value for n in adjacent))
        return ratios


def part_one(schematic: Schematic) -> int:
    return sum(number.value for number in schematic.part_numbers)


def part_two(schematic: Schematic) -> int:
    return sum(schematic.gear_ratios)


def main() -> None:
    schematic = Schematic.parse(sys.stdin.read())
    print(part_one(schematic))
    print(part_two(schematic))


if __name__ == "__main__":
    main()
