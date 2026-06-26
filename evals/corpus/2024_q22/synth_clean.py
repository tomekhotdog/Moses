"""AoC 2024 Day 22 - Monkey Market.

Part 1: sum of each buyer's 2000th secret number.
Part 2: the 4-change sequence maximizing total bananas across all buyers.
"""
from __future__ import annotations

import sys
from collections import defaultdict
from collections.abc import Iterable

PRUNE_MODULUS = 16777216  # 2**24
MULTIPLY_STEP_1 = 64
DIVIDE_STEP = 32
MULTIPLY_STEP_2 = 2048
STEPS = 2000
SEQUENCE_LENGTH = 4

Sequence = tuple[int, int, int, int]


def evolve(secret: int) -> int:
    """Advance a secret number by one pseudorandom step (mix then prune)."""
    secret = (secret ^ (secret * MULTIPLY_STEP_1)) % PRUNE_MODULUS
    secret = (secret ^ (secret // DIVIDE_STEP)) % PRUNE_MODULUS
    secret = (secret ^ (secret * MULTIPLY_STEP_2)) % PRUNE_MODULUS
    return secret


def nth_secret(initial: int, steps: int = STEPS) -> int:
    """Return the secret number after `steps` evolutions."""
    secret = initial
    for _ in range(steps):
        secret = evolve(secret)
    return secret


def price_sequence(initial: int, steps: int = STEPS) -> list[int]:
    """Return the ones-digit prices for the initial and each evolved secret."""
    secret = initial
    prices = [secret % 10]
    for _ in range(steps):
        secret = evolve(secret)
        prices.append(secret % 10)
    return prices


def part1(initials: Iterable[int]) -> int:
    return sum(nth_secret(initial) for initial in initials)


def part2(initials: Iterable[int]) -> int:
    bananas_by_sequence: dict[Sequence, int] = defaultdict(int)

    for initial in initials:
        prices = price_sequence(initial)
        changes = [b - a for a, b in zip(prices, prices[1:])]

        first_seen: set[Sequence] = set()
        for i in range(len(changes) - SEQUENCE_LENGTH + 1):
            window: Sequence = tuple(changes[i:i + SEQUENCE_LENGTH])  # type: ignore[assignment]
            if window in first_seen:
                continue
            first_seen.add(window)
            bananas_by_sequence[window] += prices[i + SEQUENCE_LENGTH]

    return max(bananas_by_sequence.values())


def parse(text: str) -> list[int]:
    return [int(line) for line in text.split()]


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "q22_example.txt"
    with open(path) as handle:
        initials = parse(handle.read())
    print(part1(initials))
    print(part2(initials))


if __name__ == "__main__":
    main()
