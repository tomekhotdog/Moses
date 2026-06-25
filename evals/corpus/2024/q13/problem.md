# AoC 2024 Day 13: Claw Contraption

Each claw machine has two buttons, A and B, that move the claw by fixed vectors. Pressing button A costs 3 tokens; pressing button B costs 1 token. Each machine has a prize at coordinates (X, Y).

The input describes machines in groups of three lines, e.g.:

```
Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400
```

**Part 1:** For each machine, find the minimum number of tokens required to win the prize, where the claw must land exactly on the prize coordinates. This reduces to solving a 2x2 linear system for non-negative integer button press counts (a, b): `a*ax + b*bx = px` and `a*ay + b*by = py`, with cost `3a + b`. Sum the costs of all winnable prizes.

**Part 2:** Add 10000000000000 to both the prize X and Y of every machine, then solve again. (The large offset makes brute force infeasible, forcing an exact linear-algebra / Cramer's-rule solution.)
