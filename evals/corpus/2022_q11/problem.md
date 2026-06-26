# Advent of Code 2022 — Day 11: "Monkey in the Middle"

Monkeys hold items, each item having a "worry level". Each monkey inspects its
items one at a time, applying an operation to the worry level (e.g. `* 19`,
`+ 6`, or `* old` which squares the value). The monkey then decides where to
throw the item based on a divisibility test, throwing it to one of two other
monkeys.

Input format (one block per monkey, blocks separated by a blank line):

```
Monkey 0:
  Starting items: 79, 98
  Operation: new = old * 19
  Test: divisible by 23
    If true: throw to monkey 2
    If false: throw to monkey 3
```

Each round, every monkey takes a full turn in order (monkey 0, then 1, ...).
During a turn the monkey inspects and throws every item it currently holds (in
order). Items thrown to a monkey later in the same round are processed in that
same round.

## Part 1
After a monkey inspects an item (applies the operation), the worry level is
divided by 3 (integer/floor division) because the item survived. Then the
divisibility test decides the target monkey. Run **20 rounds**. Count the total
number of inspections each monkey makes. The "monkey business" is the product of
the two highest inspection counts.

## Part 2
There is no longer the division by 3 after inspection, and the simulation runs
for **10000 rounds**. Worry levels would explode, so they must be kept
manageable using modular arithmetic: take the worry level modulo the product
(LCM, since the divisors are coprime primes) of all monkeys' test divisors. This
preserves every divisibility test result. Again compute the monkey business
(product of the two highest inspection counts).
