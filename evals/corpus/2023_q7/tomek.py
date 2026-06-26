from typing import List
from main import read_input
from enum import Enum
from functools import cmp_to_key


class CamelCardType(Enum):
    JOKER = 1  # Part 2.
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11  # Part 1.
    QUEEN = 12
    KING = 13
    ACE = 14


class CamelHandType(Enum):
    NOTHING = 0
    HIGH_CARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    FULL_HOUSE = 5
    FOUR_OF_A_KIND = 6
    FIVE_OF_A_KIND = 7


class CamelCard:
    def __init__(self, raw_value: str):
        self.raw_value = raw_value
        self.card_type = derive_card_type(raw_value)

    def __str__(self):
        return f"{self.raw_value}"

    def __eq__(self, other):
        # Custom equality comparison based on name and age
        if isinstance(other, CamelCard):
            return self.raw_value == other.raw_value
        return False

    def __hash__(self):
        return hash(self.raw_value)


def derive_card_type(raw_value: str):
    if raw_value == '2':
        return CamelCardType.TWO
    if raw_value == '3':
        return CamelCardType.THREE
    if raw_value == '4':
        return CamelCardType.FOUR
    if raw_value == '5':
        return CamelCardType.FIVE
    if raw_value == '6':
        return CamelCardType.SIX
    if raw_value == '7':
        return CamelCardType.SEVEN
    if raw_value == '8':
        return CamelCardType.EIGHT
    if raw_value == '9':
        return CamelCardType.NINE
    if raw_value == 'T':
        return CamelCardType.TEN
    if raw_value == 'J':
        # return CamelCardType.JACK  # Part 1.
        return CamelCardType.JOKER  # Part 2.
    if raw_value == 'Q':
        return CamelCardType.QUEEN
    if raw_value == 'K':
        return CamelCardType.KING
    if raw_value == 'A':
        return CamelCardType.ACE
    else:
        raise Exception(f"Unknown card: {raw_value}")


class CamelHand:
    def __init__(self, raw_hand: str, bid: int, use_jokers: bool):
        self.raw_hand = raw_hand
        self.bid = bid
        self.cards = [CamelCard(x) for x in raw_hand]
        if use_jokers:
            self.hand_type = derive_hand_type_with_joker(self.cards)
        else:
            self.hand_type = derive_hand_type(self.cards)

    def __str__(self):
        return f"{self.raw_hand} {self.bid}"


def derive_hand_type(cards: List[CamelCard]) -> CamelHandType:
    if len(cards) == 0:
        return CamelHandType.NOTHING

    card_counts = {}
    for card in cards:
        if card in card_counts:
            card_counts[card] += 1
        else:
            card_counts[card] = 1
    unique_cards = len(card_counts)

    fives = len(list(filter(lambda x: x == 5, card_counts.values())))
    fours = len(list(filter(lambda x: x == 4, card_counts.values())))
    threes = len(list(filter(lambda x: x == 3, card_counts.values())))
    pairs = len(list(filter(lambda x: x == 2, card_counts.values())))

    if unique_cards > 5:
        raise Exception(f"Invalid hand.!")
    if fives == 1:
        return CamelHandType.FIVE_OF_A_KIND
    if fours == 1:
        return CamelHandType.FOUR_OF_A_KIND
    if threes == 1:
        if pairs == 1:
            return CamelHandType.FULL_HOUSE
        else:
            return CamelHandType.THREE_OF_A_KIND
    if pairs == 2:
        return CamelHandType.TWO_PAIR
    if pairs == 1:
        return CamelHandType.PAIR
    else:
        return CamelHandType.HIGH_CARD


# Determine the CamelHandType that can be upgraded to by a single joker in a hand.
def joker_hand_type_upgrade(hand_type: CamelHandType) -> CamelHandType:
    if hand_type == CamelHandType.NOTHING:
        return CamelHandType.HIGH_CARD
    if hand_type == CamelHandType.HIGH_CARD:
        return CamelHandType.PAIR
    if hand_type == CamelHandType.PAIR:
        return CamelHandType.THREE_OF_A_KIND
    if hand_type == CamelHandType.TWO_PAIR:
        return CamelHandType.FULL_HOUSE
    if hand_type == CamelHandType.THREE_OF_A_KIND or hand_type == CamelHandType.FULL_HOUSE:
        return CamelHandType.FOUR_OF_A_KIND
    if hand_type == CamelHandType.FOUR_OF_A_KIND:
        return CamelHandType.FIVE_OF_A_KIND
    if hand_type == CamelHandType.FIVE_OF_A_KIND:
        return CamelHandType.FIVE_OF_A_KIND
    else:
        raise Exception(f"Unknown CamelHandType {hand_type}")


# Determine the CamelHandType when the 'J' acts like a Joker.
def derive_hand_type_with_joker(cards: List[CamelCard]) -> CamelHandType:
    non_jokers = list(filter(lambda x: x.card_type != CamelCardType.JOKER, cards))
    upgraded_hand_type = derive_hand_type(non_jokers)
    jokers = len(cards) - len(non_jokers)
    while jokers > 0:
        upgraded_hand_type = joker_hand_type_upgrade(upgraded_hand_type)
        jokers -= 1
    return upgraded_hand_type


def hand_comparison_part(hand1: CamelHand, hand2: CamelHand):
    if hand1.hand_type.value != hand2.hand_type.value:
        return hand1.hand_type.value - hand2.hand_type.value
    for idx in range(len(hand1.cards)):
        if hand1.cards[idx] != hand2.cards[idx]:
            return hand1.cards[idx].card_type.value - hand2.cards[idx].card_type.value


def parse_input(filename: str, use_jokers: bool) -> List[CamelHand]:
    raw_hands = read_input(filename)
    hands = []
    for raw_hand in raw_hands:
        elems = raw_hand.split(' ')
        hands.append(CamelHand(elems[0].strip(), int(elems[1].strip()), use_jokers))
    return hands


def part1() -> int:
    hands = parse_input('q7.txt', False)
    hands = sorted(hands, key=cmp_to_key(hand_comparison_part))
    return sum([hand.bid * (index + 1) for index, hand in enumerate(hands)])


def part2() -> int:
    hands = parse_input('q7.txt', True)
    hands = sorted(hands, key=cmp_to_key(hand_comparison_part))
    return sum([hand.bid * (index + 1) for index, hand in enumerate(hands)])
