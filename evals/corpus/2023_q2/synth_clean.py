"""Advent of Code 2023, Day 2 — Cube Conundrum.

A clean, typed solution built around explicit ``Reveal`` and ``Game``
abstractions. Cube colours and bag limits are named constants, so there are
no magic numbers buried in the logic.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from math import prod
from typing import Iterable

RED, GREEN, BLUE = "red", "green", "blue"
COLOURS = (RED, GREEN, BLUE)

# The bag the elf claims to be drawing from in Part 1.
BAG_LIMITS: dict[str, int] = {RED: 12, GREEN: 13, BLUE: 14}


@dataclass(frozen=True)
class Reveal:
    """A single handful of cubes shown during a game."""

    counts: dict[str, int]

    def count(self, colour: str) -> int:
        return self.counts.get(colour, 0)

    def fits_within(self, limits: dict[str, int]) -> bool:
        return all(self.count(c) <= limits[c] for c in COLOURS)


@dataclass(frozen=True)
class Game:
    game_id: int
    reveals: tuple[Reveal, ...]

    def is_possible(self, limits: dict[str, int]) -> bool:
        """True if every reveal fits within ``limits``."""
        return all(reveal.fits_within(limits) for reveal in self.reveals)

    def minimum_set(self) -> dict[str, int]:
        """The fewest cubes of each colour that make this game possible."""
        return {
            colour: max(reveal.count(colour) for reveal in self.reveals)
            for colour in COLOURS
        }

    def power(self) -> int:
        return prod(self.minimum_set().values())


def parse_reveal(text: str) -> Reveal:
    counts: dict[str, int] = {}
    for entry in text.split(","):
        amount, colour = entry.split()
        counts[colour] = int(amount)
    return Reveal(counts)


def parse_game(line: str) -> Game:
    header, body = line.split(":")
    game_id = int(header.split()[1])
    reveals = tuple(parse_reveal(part) for part in body.split(";"))
    return Game(game_id, reveals)


def parse_games(lines: Iterable[str]) -> list[Game]:
    return [parse_game(line) for line in lines if line.strip()]


def part_one(games: list[Game]) -> int:
    return sum(game.game_id for game in games if game.is_possible(BAG_LIMITS))


def part_two(games: list[Game]) -> int:
    return sum(game.power() for game in games)


def main(path: str) -> None:
    with open(path, encoding="utf-8") as f:
        games = parse_games(f)
    print(part_one(games))
    print(part_two(games))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "input.txt")
