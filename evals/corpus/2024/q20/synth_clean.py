"""Advent of Code 2024, Day 20: Race Condition.

The track is a single (unbranching) path, so a single BFS from the start
assigns every track tile its distance along the route. A "cheat" jumps from
one track tile to another through walls; because the start tile's distance is
fixed, the time saved by a cheat is simply the difference of the two tiles'
route distances minus the Manhattan distance travelled during the cheat.
"""

from __future__ import annotations

import sys
from collections import deque

Point = tuple[int, int]
DistanceMap = dict[Point, int]

WALL = "#"
START = "S"
END = "E"
ORTHOGONAL_STEPS = ((0, 1), (0, -1), (1, 0), (-1, 0))

PART1_MAX_CHEAT = 2
PART2_MAX_CHEAT = 20
DEFAULT_MIN_SAVING = 100


def parse_grid(text: str) -> tuple[list[str], Point]:
    """Return the grid rows and the start tile."""
    grid = text.splitlines()
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell == START:
                return grid, (y, x)
    raise ValueError("no start tile found")


def route_distances(grid: list[str], start: Point) -> DistanceMap:
    """BFS from the start, mapping each track tile to its distance along the route."""
    distances: DistanceMap = {start: 0}
    queue: deque[Point] = deque([start])
    while queue:
        y, x = queue.popleft()
        for dy, dx in ORTHOGONAL_STEPS:
            neighbour = (y + dy, x + dx)
            ny, nx = neighbour
            if not (0 <= ny < len(grid) and 0 <= nx < len(grid[ny])):
                continue
            if grid[ny][nx] == WALL or neighbour in distances:
                continue
            distances[neighbour] = distances[(y, x)] + 1
            queue.append(neighbour)
    return distances


def count_cheats(
    distances: DistanceMap,
    max_cheat_length: int,
    min_saving: int = DEFAULT_MIN_SAVING,
) -> int:
    """Count cheats of length up to ``max_cheat_length`` saving at least ``min_saving``."""
    tiles = list(distances.items())
    count = 0
    for start_tile, start_dist in tiles:
        sy, sx = start_tile
        for end_tile, end_dist in tiles:
            ey, ex = end_tile
            cheat_length = abs(sy - ey) + abs(sx - ex)
            if not 1 <= cheat_length <= max_cheat_length:
                continue
            if end_dist - start_dist - cheat_length >= min_saving:
                count += 1
    return count


def solve(text: str, min_saving: int = DEFAULT_MIN_SAVING) -> tuple[int, int]:
    grid, start = parse_grid(text)
    distances = route_distances(grid, start)
    part1 = count_cheats(distances, PART1_MAX_CHEAT, min_saving)
    part2 = count_cheats(distances, PART2_MAX_CHEAT, min_saving)
    return part1, part2


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "q20.txt"
    with open(path, encoding="utf-8") as handle:
        part1, part2 = solve(handle.read())
    print(part1)
    print(part2)


if __name__ == "__main__":
    main()
