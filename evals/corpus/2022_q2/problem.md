# AoC 2022 Day 2 — Rock Paper Scissors

A strategy guide lists rounds of Rock Paper Scissors. Each line has two columns
separated by a space. The first column is the opponent's shape: `A` = Rock,
`B` = Paper, `C` = Scissors.

## Part 1

The second column is **your shape**: `X` = Rock, `Y` = Paper, `Z` = Scissors.

Score each round as the sum of:

- the **shape score** for the shape you played: Rock = 1, Paper = 2, Scissors = 3
- the **outcome score**: loss = 0, draw = 3, win = 6

(Rock beats Scissors, Scissors beats Paper, Paper beats Rock; equal shapes draw.)

Sum the per-round scores across all rounds.

## Part 2

The second column is instead the **required outcome**: `X` = you must lose,
`Y` = you must draw, `Z` = you must win.

Pick the shape that achieves the required outcome against the opponent, then
score the round exactly as in Part 1 (shape score + outcome score). Sum across
all rounds.

## Example

```
A Y
B X
C Z
```

Part 1 total = 15. Part 2 total = 12.
