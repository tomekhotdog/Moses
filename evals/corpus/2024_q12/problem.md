# AoC 2024 Day 12: Garden Groups

The input is a grid of plant types (single letters). Contiguous cells of the same
type, connected orthogonally (up/down/left/right), form a **region**.

**Part 1:** For each region compute its area (number of cells) multiplied by its
perimeter (number of cell edges that border a different type or the grid edge),
then sum these products across all regions.

**Part 2:** For each region compute its area multiplied by the number of sides it
has (straight fence segments). The number of sides of a region equals its number
of corners. Sum these products across all regions.

For the example grid in `example3.txt`, Part 1 is `1930` and Part 2 is `1206`.
