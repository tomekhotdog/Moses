from collections import Counter
from functools import cmp_to_key

CARD_ORDER_P1 = "23456789TJQKA"
CARD_ORDER_P2 = "J23456789TQKA"


def hand_type(cards, use_joker):
    counts = Counter(cards)
    if use_joker and "J" in counts and len(counts) > 1:
        jokers = counts.pop("J")
        top = counts.most_common(1)[0][0]
        counts[top] += jokers

    sizes = sorted(counts.values(), reverse=True)
    if sizes == [5]:
        return 6
    if sizes == [4, 1]:
        return 5
    if sizes == [3, 2]:
        return 4
    if sizes == [3, 1, 1]:
        return 3
    if sizes == [2, 2, 1]:
        return 2
    if sizes == [2, 1, 1, 1]:
        return 1
    return 0


def make_comparator(use_joker):
    order = CARD_ORDER_P2 if use_joker else CARD_ORDER_P1

    def compare(a, b):
        type_a = hand_type(a[0], use_joker)
        type_b = hand_type(b[0], use_joker)
        if type_a != type_b:
            return type_a - type_b
        for card_a, card_b in zip(a[0], b[0]):
            if card_a != card_b:
                return order.index(card_a) - order.index(card_b)
        return 0

    return compare


def parse(lines):
    hands = []
    for line in lines:
        cards, bid = line.split()
        hands.append((cards, int(bid)))
    return hands


def total_winnings(hands, use_joker):
    ranked = sorted(hands, key=cmp_to_key(make_comparator(use_joker)))
    return sum((i + 1) * bid for i, (_, bid) in enumerate(ranked))


def main():
    with open("input.txt") as f:
        hands = parse(f.read().strip().splitlines())
    print(total_winnings(hands, use_joker=False))
    print(total_winnings(hands, use_joker=True))


if __name__ == "__main__":
    main()
