# Advent of Code 2023, Day 3
# (c) blu3r4y
# Source: https://github.com/blu3r4y/AdventOfCode2023 (src/day3.py)

from collections import defaultdict
from functools import reduce
from operator import mul

from aocd.models import Puzzle
from funcy import print_calls, print_durations


@print_calls
@print_durations(unit="ms")
def part1(grid):
    numbers, symbols, _ = grid
    total = 0

    for y, xrange in numbers.items():
        for (xstart, xend), cell in xrange.items():
            is_part_number = False

            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue

                    # check if the adjacent cell is a symbol
                    for x in range(xstart, xend + 1):
                        if (y + dy, x + dx) in symbols:
                            is_part_number = True

            if is_part_number:
                total += cell

    return total


@print_calls
@print_durations(unit="ms")
def part2(grid):
    numbers, _, gears = grid
    total = 0

    for gy, gx in gears:
        adjacents = set()

        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue

                # check the ranges of the adjacent numbers
                x, y = gx + dx, gy + dy
                for (nxstart, nxend), cell in numbers[y].items():
                    if nxstart <= x <= nxend:
                        adjacents.add(cell)

        if len(adjacents) == 2:
            total += reduce(mul, adjacents)

    return total


def load(data):
    numbers, symbols, gears = defaultdict(dict), set(), set()

    for y, line in enumerate(data.split("\n")):
        x, xstart, buffer = 0, None, ""
        while x < len(line):
            cell = line[x]
            if cell.isnumeric():
                # handle starting point of a number
                # and incrementally buffer the number
                if buffer == "":
                    xstart = x
                buffer += cell

            else:
                if buffer:
                    # store the number and reset the buffer
                    numbers[y][(xstart, x - 1)] = int(buffer)
                    xstart, buffer = None, ""

                if cell != ".":
                    # store symbols
                    symbols.add((y, x))
                    if cell == "*":
                        gears.add((y, x))

            x += 1

        if buffer:
            # handle numbers at the end of the line
            numbers[y][(xstart, x - 1)] = int(buffer)

    return numbers, symbols, gears


if __name__ == "__main__":
    puzzle = Puzzle(year=2023, day=3)

    ans1 = part1(load(puzzle.input_data))
    assert ans1 == 543867
    puzzle.answer_a = ans1

    ans2 = part2(load(puzzle.input_data))
    assert ans2 == 79613331
    puzzle.answer_b = ans2
