"""Advent of Code 2022, Day 2 — Rock Paper Scissors.

Models the game with explicit domain types (Shape, Outcome) so that scoring and
the two decryption strategies read as direct statements of the rules.
"""

from __future__ import annotations

import sys
from enum import Enum
from pathlib import Path


class Shape(Enum):
    """A hand shape, carrying its intrinsic round score (1/2/3)."""

    ROCK = 1
    PAPER = 2
    SCISSORS = 3

    @property
    def defeats(self) -> "Shape":
        """The shape this one beats."""
        return _BEATS[self]

    @property
    def defeated_by(self) -> "Shape":
        """The shape that beats this one."""
        return _BEATEN_BY[self]


class Outcome(Enum):
    """The result of a round from our perspective, carrying its score (0/3/6)."""

    LOSS = 0
    DRAW = 3
    WIN = 6


_BEATS: dict[Shape, Shape] = {
    Shape.ROCK: Shape.SCISSORS,
    Shape.PAPER: Shape.ROCK,
    Shape.SCISSORS: Shape.PAPER,
}
_BEATEN_BY: dict[Shape, Shape] = {beaten: winner for winner, beaten in _BEATS.items()}

_OPPONENT_CODES: dict[str, Shape] = {"A": Shape.ROCK, "B": Shape.PAPER, "C": Shape.SCISSORS}
_SHAPE_CODES: dict[str, Shape] = {"X": Shape.ROCK, "Y": Shape.PAPER, "Z": Shape.SCISSORS}
_OUTCOME_CODES: dict[str, Outcome] = {"X": Outcome.LOSS, "Y": Outcome.DRAW, "Z": Outcome.WIN}


def outcome_against(opponent: Shape, me: Shape) -> Outcome:
    """The outcome for ``me`` when facing ``opponent``."""
    if me == opponent:
        return Outcome.DRAW
    return Outcome.WIN if opponent.defeated_by == me else Outcome.LOSS


def shape_for_outcome(opponent: Shape, desired: Outcome) -> Shape:
    """The shape ``me`` must play to achieve ``desired`` against ``opponent``."""
    match desired:
        case Outcome.DRAW:
            return opponent
        case Outcome.WIN:
            return opponent.defeated_by
        case Outcome.LOSS:
            return opponent.defeats


def score_round(opponent: Shape, me: Shape) -> int:
    """Total round score: shape score plus outcome score."""
    return me.value + outcome_against(opponent, me).value


def parse_guide(text: str) -> list[tuple[str, str]]:
    """Split the strategy guide into (opponent_code, second_code) pairs."""
    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        left, right = line.split()
        pairs.append((left, right))
    return pairs


def part1(guide: list[tuple[str, str]]) -> int:
    """Second column names our shape directly."""
    return sum(
        score_round(_OPPONENT_CODES[left], _SHAPE_CODES[right]) for left, right in guide
    )


def part2(guide: list[tuple[str, str]]) -> int:
    """Second column names the required outcome; derive the shape to play."""
    total = 0
    for left, right in guide:
        opponent = _OPPONENT_CODES[left]
        me = shape_for_outcome(opponent, _OUTCOME_CODES[right])
        total += score_round(opponent, me)
    return total


def main(path: str) -> None:
    guide = parse_guide(Path(path).read_text())
    print(part1(guide))
    print(part2(guide))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "input.txt")
