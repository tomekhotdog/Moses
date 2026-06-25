"""Advent of Code 2024, Day 13: Claw Contraption.

Each claw machine is a 2x2 linear system. We solve it exactly with Cramer's
rule and accept a machine only when the button-press counts are non-negative
integers.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass

COST_A = 3
COST_B = 1
PART2_OFFSET = 10_000_000_000_000

_MACHINE_PATTERN = re.compile(
    r"Button A: X\+(\d+), Y\+(\d+)\s+"
    r"Button B: X\+(\d+), Y\+(\d+)\s+"
    r"Prize: X=(\d+), Y=(\d+)"
)


@dataclass(frozen=True)
class Machine:
    """A claw machine: two button vectors and a prize coordinate."""

    a: tuple[int, int]
    b: tuple[int, int]
    prize: tuple[int, int]

    def with_offset(self, offset: int) -> "Machine":
        """Return a copy with the prize shifted by `offset` on both axes."""
        px, py = self.prize
        return Machine(self.a, self.b, (px + offset, py + offset))


def parse_machines(text: str) -> list[Machine]:
    """Parse the full puzzle input into a list of machines."""
    machines = []
    for ax, ay, bx, by, px, py in _MACHINE_PATTERN.findall(text):
        machines.append(
            Machine(
                a=(int(ax), int(ay)),
                b=(int(bx), int(by)),
                prize=(int(px), int(py)),
            )
        )
    return machines


def solve(machine: Machine) -> int | None:
    """Return the token cost to win, or None if the prize is unwinnable.

    Solves a*A + b*B = prize via Cramer's rule. A solution is valid only when
    both press counts are non-negative integers.
    """
    ax, ay = machine.a
    bx, by = machine.b
    px, py = machine.prize

    determinant = ax * by - ay * bx
    if determinant == 0:
        return None

    numerator_a = px * by - py * bx
    numerator_b = ax * py - ay * px

    if numerator_a % determinant != 0 or numerator_b % determinant != 0:
        return None

    presses_a = numerator_a // determinant
    presses_b = numerator_b // determinant
    if presses_a < 0 or presses_b < 0:
        return None

    return COST_A * presses_a + COST_B * presses_b


def total_cost(machines: list[Machine]) -> int:
    """Sum the token cost over all winnable machines."""
    return sum(cost for m in machines if (cost := solve(m)) is not None)


def part1(machines: list[Machine]) -> int:
    return total_cost(machines)


def part2(machines: list[Machine]) -> int:
    shifted = [m.with_offset(PART2_OFFSET) for m in machines]
    return total_cost(shifted)


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "q13_example.txt"
    with open(path, encoding="utf-8") as handle:
        machines = parse_machines(handle.read())
    print(part1(machines))
    print(part2(machines))


if __name__ == "__main__":
    main()
