# AoC 2023 Day 11 — Cosmic Expansion

A grid of galaxies (`#`) and empty space (`.`). Every completely-empty row and
column is expanded (counts as more than one).

**Part 1:** After doubling every empty row/column (each empty row/col counts as
2), sum the shortest (Manhattan) distances between every pair of galaxies.

**Part 2:** Empty rows/columns each count as 1,000,000. Sum the pairwise
distances again — computed via coordinate expansion, not by literally growing
the grid.

The shortest path between two galaxies is the Manhattan distance measured in the
expanded universe. Equivalently, for each pair, take the raw Manhattan distance
and add `(factor - 1)` for every empty row and empty column strictly between
them.
