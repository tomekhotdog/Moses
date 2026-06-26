"""Advent of Code 2022, Day 11: Monkey in the Middle."""

from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from typing import Callable

PART1_ROUNDS = 20
PART2_ROUNDS = 10_000
WORRY_RELIEF_DIVISOR = 3
TOP_INSPECTORS = 2


@dataclass
class Monkey:
    """A single monkey with its items, inspection rule and routing logic."""

    items: list[int]
    operation: Callable[[int], int]
    divisor: int
    if_true: int
    if_false: int
    inspections: int = field(default=0)

    def target_for(self, worry: int) -> int:
        """Return the index of the monkey that should receive ``worry``."""
        return self.if_true if worry % self.divisor == 0 else self.if_false


def _parse_operation(expression: str) -> Callable[[int], int]:
    """Build a worry-update function from e.g. ``old * 19`` or ``old * old``."""
    left, operator, right = expression.split()

    def apply(old: int) -> int:
        operand = old if right == "old" else int(right)
        return old * operand if operator == "*" else old + operand

    return apply


def parse_monkeys(text: str) -> list[Monkey]:
    """Parse the puzzle input into a list of :class:`Monkey` objects."""
    monkeys: list[Monkey] = []
    for block in text.strip().split("\n\n"):
        lines = [line.strip() for line in block.splitlines()]
        items = [int(n) for n in lines[1].split(":")[1].split(",")]
        operation = _parse_operation(lines[2].split("=")[1].strip())
        divisor = int(lines[3].split()[-1])
        if_true = int(lines[4].split()[-1])
        if_false = int(lines[5].split()[-1])
        monkeys.append(Monkey(items, operation, divisor, if_true, if_false))
    return monkeys


def monkey_business(monkeys: list[Monkey], rounds: int, relief: bool) -> int:
    """Simulate ``rounds`` rounds and return the product of the two busiest counts.

    When ``relief`` is true (part 1) worry is floor-divided by 3 after each
    inspection. Otherwise (part 2) worry is reduced modulo the product of all
    divisors, which keeps every divisibility test intact while bounding growth.
    """
    modulus = math.prod(monkey.divisor for monkey in monkeys)

    for _ in range(rounds):
        for monkey in monkeys:
            for worry in monkey.items:
                monkey.inspections += 1
                worry = monkey.operation(worry)
                worry = worry // WORRY_RELIEF_DIVISOR if relief else worry % modulus
                monkeys[monkey.target_for(worry)].items.append(worry)
            monkey.items = []

    busiest = sorted(monkey.inspections for monkey in monkeys)
    return math.prod(busiest[-TOP_INSPECTORS:])


def part1(text: str) -> int:
    return monkey_business(parse_monkeys(text), PART1_ROUNDS, relief=True)


def part2(text: str) -> int:
    return monkey_business(parse_monkeys(text), PART2_ROUNDS, relief=False)


def main(path: str) -> None:
    text = open(path).read()
    print(part1(text))
    print(part2(text))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "input.txt")
