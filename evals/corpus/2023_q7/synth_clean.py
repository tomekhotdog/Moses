"""Advent of Code 2023, Day 7: Camel Cards.

Ranks poker-like hands by type then by individual card strength, optionally
treating ``J`` as a wildcard joker, and sums ``bid * rank`` over all hands.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path
from typing import Iterable


class HandType(IntEnum):
    """Hand categories ordered weakest (HIGH_CARD) to strongest (FIVE_OF_A_KIND)."""

    HIGH_CARD = 0
    ONE_PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    FULL_HOUSE = 4
    FOUR_OF_A_KIND = 5
    FIVE_OF_A_KIND = 6


# Maps a sorted-descending tuple of card multiplicities to its hand type.
_SHAPE_TO_TYPE: dict[tuple[int, ...], HandType] = {
    (5,): HandType.FIVE_OF_A_KIND,
    (4, 1): HandType.FOUR_OF_A_KIND,
    (3, 2): HandType.FULL_HOUSE,
    (3, 1, 1): HandType.THREE_OF_A_KIND,
    (2, 2, 1): HandType.TWO_PAIR,
    (2, 1, 1, 1): HandType.ONE_PAIR,
    (1, 1, 1, 1, 1): HandType.HIGH_CARD,
}

# Card strength orders, weakest first; index gives the comparison rank.
_ORDER_STANDARD = "23456789TJQKA"
_ORDER_JOKER = "J23456789TQKA"

JOKER = "J"
HAND_SIZE = 5


def _hand_shape(cards: str) -> tuple[int, ...]:
    """Multiplicities of distinct cards, sorted descending."""
    return tuple(sorted(Counter(cards).values(), reverse=True))


def classify(cards: str, *, jokers_wild: bool) -> HandType:
    """Determine the best hand type, optionally treating ``J`` as a wildcard.

    With ``jokers_wild`` the optimal play always adds every joker to the most
    common non-joker card, which maximises the dominant multiplicity.
    """
    if not jokers_wild or JOKER not in cards:
        return _SHAPE_TO_TYPE[_hand_shape(cards)]

    joker_count = cards.count(JOKER)
    if joker_count == HAND_SIZE:
        return HandType.FIVE_OF_A_KIND

    counts = Counter(cards.replace(JOKER, ""))
    best_card, _ = counts.most_common(1)[0]
    return _SHAPE_TO_TYPE[_hand_shape(cards.replace(JOKER, best_card))]


@dataclass(frozen=True)
class Hand:
    """A five-card hand with its bid and chosen scoring rules."""

    cards: str
    bid: int
    jokers_wild: bool

    @property
    def hand_type(self) -> HandType:
        return classify(self.cards, jokers_wild=self.jokers_wild)

    @property
    def sort_key(self) -> tuple[int, tuple[int, ...]]:
        order = _ORDER_JOKER if self.jokers_wild else _ORDER_STANDARD
        card_strengths = tuple(order.index(card) for card in self.cards)
        return (int(self.hand_type), card_strengths)


def parse(lines: Iterable[str], *, jokers_wild: bool) -> list[Hand]:
    hands = []
    for line in lines:
        cards, bid = line.split()
        hands.append(Hand(cards=cards, bid=int(bid), jokers_wild=jokers_wild))
    return hands


def total_winnings(hands: list[Hand]) -> int:
    ranked = sorted(hands, key=lambda hand: hand.sort_key)
    return sum(rank * hand.bid for rank, hand in enumerate(ranked, start=1))


def solve(lines: list[str], *, jokers_wild: bool) -> int:
    return total_winnings(parse(lines, jokers_wild=jokers_wild))


def main() -> None:
    lines = Path("input.txt").read_text().strip().splitlines()
    print(solve(lines, jokers_wild=False))
    print(solve(lines, jokers_wild=True))


if __name__ == "__main__":
    main()
