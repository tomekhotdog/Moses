"""Advent of Code 2024, Day 14 — Restroom Redoubt.

Part 1: simulate 100 seconds and compute the safety factor (product of the
robot counts in the four quadrants, ignoring robots on the centre lines).

Part 2: locate the Christmas tree by finding the second whose layout has the
lowest spatial variance — when the robots cluster into the picture they are far
less spread out than in any random frame.
"""

from __future__ import annotations

import math
import re
import sys
from dataclasses import dataclass
from statistics import pvariance

GRID_WIDTH = 101
GRID_HEIGHT = 103
PART1_SECONDS = 100


@dataclass(frozen=True)
class Robot:
    x: int
    y: int
    dx: int
    dy: int

    def position_after(self, seconds: int, width: int, height: int) -> tuple[int, int]:
        """Return the robot's wrapped (x, y) after `seconds` of movement."""
        return (
            (self.x + self.dx * seconds) % width,
            (self.y + self.dy * seconds) % height,
        )


def parse_robots(text: str) -> list[Robot]:
    robots: list[Robot] = []
    for line in text.strip().splitlines():
        x, y, dx, dy = (int(n) for n in re.findall(r"-?\d+", line))
        robots.append(Robot(x, y, dx, dy))
    return robots


def safety_factor(robots: list[Robot], seconds: int, width: int, height: int) -> int:
    """Product of robot counts per quadrant; centre row/column are excluded."""
    mid_x, mid_y = width // 2, height // 2
    quadrants = [0, 0, 0, 0]
    for robot in robots:
        x, y = robot.position_after(seconds, width, height)
        if x == mid_x or y == mid_y:
            continue
        index = (1 if x > mid_x else 0) + (2 if y > mid_y else 0)
        quadrants[index] += 1
    return math.prod(quadrants)


def _spread(robots: list[Robot], seconds: int, width: int, height: int) -> float:
    """Combined positional variance at a given second (lower means clustered)."""
    positions = [r.position_after(seconds, width, height) for r in robots]
    xs = [x for x, _ in positions]
    ys = [y for _, y in positions]
    return pvariance(xs) + pvariance(ys)


def find_tree(robots: list[Robot], width: int, height: int) -> int:
    """The layout repeats every width*height seconds; pick the least-spread one."""
    period = width * height
    return min(range(period), key=lambda t: _spread(robots, t, width, height))


def main() -> None:
    path = sys.argv[1] if len(sys.argv) > 1 else "q14.txt"
    robots = parse_robots(open(path).read())

    print("Part 1:", safety_factor(robots, PART1_SECONDS, GRID_WIDTH, GRID_HEIGHT))
    print("Part 2:", find_tree(robots, GRID_WIDTH, GRID_HEIGHT))


if __name__ == "__main__":
    main()
