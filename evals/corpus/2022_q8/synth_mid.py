"""AoC 2022 Day 8 — decent, readable, but not abstracted into Grid/Point."""

import math


def parse(path):
    grid = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                grid.append([int(c) for c in line])
    return grid


def line_of_sight(grid, r, c, dr, dc):
    """Heights from (r, c) outward in direction (dr, dc), exclusive."""
    rows, cols = len(grid), len(grid[0])
    r, c = r + dr, c + dc
    while 0 <= r < rows and 0 <= c < cols:
        yield grid[r][c]
        r, c = r + dr, c + dc


DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def is_visible(grid, r, c):
    height = grid[r][c]
    for dr, dc in DIRECTIONS:
        if all(h < height for h in line_of_sight(grid, r, c, dr, dc)):
            return True
    return False


def scenic_score(grid, r, c):
    height = grid[r][c]
    score = 1
    for dr, dc in DIRECTIONS:
        distance = 0
        for h in line_of_sight(grid, r, c, dr, dc):
            distance += 1
            if h >= height:
                break
        score *= distance
    return score


def main(path="input.txt"):
    grid = parse(path)
    rows, cols = len(grid), len(grid[0])
    visible = sum(
        is_visible(grid, r, c) for r in range(rows) for c in range(cols)
    )
    best = max(
        scenic_score(grid, r, c) for r in range(rows) for c in range(cols)
    )
    print(visible)
    print(best)


if __name__ == "__main__":
    main()
