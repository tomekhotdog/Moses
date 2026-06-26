# AoC 2022 Day 8 — Treetop Tree House

Input is a grid of tree heights, one digit (0-9) per cell.

## Part 1
Count the trees visible from outside the grid. A tree is visible if all
trees between it and at least one edge of the grid — along its row or its
column — are strictly shorter than it. All trees on the edge of the grid
are visible.

## Part 2
A tree's "scenic score" is the product of its viewing distances in the four
directions (up, down, left, right). The viewing distance in a direction is
the number of trees seen before the line of sight is blocked, i.e. counting
trees until (and including) the first tree of equal or greater height, or
until the edge of the grid. Find the highest scenic score of any tree.
