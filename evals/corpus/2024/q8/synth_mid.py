import sys
from itertools import combinations


def parse(path):
    with open(path) as f:
        grid = [line for line in f.read().splitlines() if line]
    antennas = {}
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch != ".":
                antennas.setdefault(ch, []).append((r, c))
    return grid, antennas


def in_bounds(grid, r, c):
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def solve(path):
    grid, antennas = parse(path)
    part1 = set()
    part2 = set()
    for points in antennas.values():
        for (r1, c1), (r2, c2) in combinations(points, 2):
            dr, dc = r2 - r1, c2 - c1
            # Part 1: one step beyond each antenna.
            for r, c in [(r1 - dr, c1 - dc), (r2 + dr, c2 + dc)]:
                if in_bounds(grid, r, c):
                    part1.add((r, c))
            # Part 2: walk the full line both ways from each antenna.
            for sr, sc, step_r, step_c in [(r1, c1, -dr, -dc), (r2, c2, dr, dc)]:
                r, c = sr, sc
                while in_bounds(grid, r, c):
                    part2.add((r, c))
                    r, c = r + step_r, c + step_c
    return len(part1), len(part2)


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "q8.txt"
    p1, p2 = solve(path)
    print(p1)
    print(p2)
