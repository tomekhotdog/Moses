# AoC 2023 Day 7: Camel Cards

A poker-like game. Each hand of 5 cards has a **type** (from strongest to weakest):
five-of-a-kind, four-of-a-kind, full house, three-of-a-kind, two-pair, one-pair,
high-card.

Hands are ranked first by type, then — to break ties between hands of the same
type — by comparing cards left-to-right by individual strength (the first
position where they differ decides). Each hand has a **bid**. The total
**winnings** = sum over all hands of `bid * rank`, where rank 1 is the weakest
hand and rank N (number of hands) is the strongest.

**Part 1** uses card order, strongest to weakest: `A, K, Q, J, T, 9, 8, 7, 6, 5, 4, 3, 2`.

**Part 2** turns `J` into a **Joker**: it becomes the *weakest* individual card
(below `2`) for the tie-break comparison, but acts as a *wildcard* that counts as
whichever card maximizes the hand's type. Recompute each hand's type with the
jokers chosen optimally, then rank and sum winnings exactly as in Part 1.
