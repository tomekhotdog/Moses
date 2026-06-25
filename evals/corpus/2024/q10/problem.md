# AoC 2024 Day 10: Hoof It

The input is a topographic map: a grid of single-digit heights 0-9. A hiking
trail starts at a height of 0, ends at a height of 9, and always increases by
exactly 1 at each step, moving only up, down, left, or right (no diagonals).

A **trailhead** is any position with height 0.

**Part 1:** A trailhead's *score* is the number of distinct height-9 cells
reachable from it by valid hiking trails. Sum the scores of all trailheads.

**Part 2:** A trailhead's *rating* is the number of distinct hiking trails
(distinct paths) that begin at that trailhead. Sum the ratings of all
trailheads.

Example grid:

```
0123
1234
8765
9876
```

For this example the sum of scores (Part 1) is 1 and the sum of ratings
(Part 2) is 16.
