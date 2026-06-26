# Source: blu3r4y/AdventOfCode2023 (src/day11.py), mined online.
from itertools import combinations

from aocd.models import Puzzle
from funcy import print_calls, print_durations


@print_calls
@print_durations(unit="ms")
def part1(galaxies):
    return total_pairwise_distances(galaxies, factor=1)


@print_calls
@print_durations(unit="ms")
def part2(galaxies, factor=999999):
    return total_pairwise_distances(galaxies, factor=factor)


def total_pairwise_distances(galaxies, factor):
    galaxies = expand_universe(galaxies, factor)

    total = 0
    for (ax, ay), (bx, by) in combinations(galaxies, 2):
        dist = abs(ax - bx) + abs(ay - by)
        total += dist

    return total


def expand_universe(galaxies, factor=1):
    xs = set(x for x, _ in galaxies)
    ys = set(y for _, y in galaxies)
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    # rows and columns without any galaxies
    xempty = set(range(xmin, xmax + 1)) - xs
    yempty = set(range(ymin, ymax + 1)) - ys

    new_galaxies = set()
    for x, y in sorted(galaxies):
        xidx = sum(1 for xe in xempty if x > xe)
        yidx = sum(1 for ye in yempty if y > ye)

        new_galaxies.add((x + xidx * factor, y + yidx * factor))

    return new_galaxies


def load(data):
    galaxies = set()

    for y, line in enumerate(data.split("\n")):
        for x, char in enumerate(line):
            if char == "#":
                galaxies.add((x, y))

    return galaxies


if __name__ == "__main__":
    puzzle = Puzzle(year=2023, day=11)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 9965032
    puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 550358864332
    puzzle.answer_b = ans2
