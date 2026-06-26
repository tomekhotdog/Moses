# Advent of Code 2024, Day 16: Reindeer Maze

You are given a grid maze where `#` are walls, `S` is the start tile (the reindeer begins there facing East), and `E` is the end tile. The reindeer can move forward one tile in its current facing for a cost of 1, or rotate 90 degrees left or right in place for a cost of 1000.

**Part 1:** Find the lowest total cost to reach `E` from `S`. This is a Dijkstra / uniform-cost search over states of (position, facing).

**Part 2:** Count the number of distinct tiles that lie on at least one lowest-cost path from `S` to `E`.
