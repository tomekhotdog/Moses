from main import read_input
from enum import Enum

class Direction(Enum):
    N = 1
    NE = 2
    E = 3
    SE = 4
    S = 5
    SW = 6
    W = 7
    NW = 8

def read_grid(filename: str) -> [[]]:
    wordsearch = read_input(filename)
    width = len(wordsearch[0])
    height = len(wordsearch)
    grid = [['.' for _ in range(width)] for _ in range(height)]
    for x in range(width):
        for y in range(height):
            grid[x][height - y - 1] = wordsearch[y][x]
    return grid

def print_grid(grid: [[]]):
    height = len(grid)
    for y in range(height):
        line = ''
        for x in range(len(grid[0])):
            line += grid[x][height - y - 1]
        print(line)

def assert_location(grid, x: int, y: int, expected: chr) -> bool:
    if x >= len(grid[0]) or x < 0 or y >= len(grid) or y < 0:
        return False
    return grid[x][y] == expected

def assert_locations(grid, x: int, y: int, xs: [int], ys: [int], expected_chars: [chr]) -> bool:
    assert(len(xs) == len(ys) and
           len(xs) == len(ys))
    return all([assert_location(grid, x + xs[i], y + ys[i], expected_chars[i]) for i in range(len(xs))])

def search_path(grid, x: int, y: int, word, direction: Direction) -> bool:
    if direction == Direction.N:
        return assert_locations(grid, x, y, [0, 0, 0, 0], [0, 1, 2, 3], word)
    elif direction == Direction.NE:
        return assert_locations(grid, x, y, [0, 1, 2, 3], [0, 1, 2, 3], word)
    elif direction == Direction.E:
        return assert_locations(grid, x, y, [0, 1, 2, 3], [0, 0, 0, 0], word)
    elif direction == Direction.SE:
        return assert_locations(grid, x, y, [0, 1, 2, 3], [0, -1, -2, -3], word)
    elif direction == Direction.S:
        return assert_locations(grid, x, y, [0, 0, 0, 0], [0, -1, -2, -3], word)
    elif direction == Direction.SW:
        return assert_locations(grid, x, y, [0, -1, -2, -3], [0, -1, -2, -3], word)
    elif direction == Direction.W:
        return assert_locations(grid, x, y, [0, -1, -2, -3], [0, 0, 0, 0], word)
    elif direction == Direction.NW:
        return assert_locations(grid, x, y, [0, -1, -2, -3], [0, 1, 2, 3], word)

def search_location_part_1(grid, x: int, y: int, word) -> int:
    directions = [Direction.N, Direction.NE, Direction.E, Direction.SE,
                  Direction.S, Direction.SW, Direction.W, Direction.NW]
    return len(list(filter(lambda d: search_path(grid, x, y, word, d), directions)))

def part1() -> int:
    grid = read_grid('q4.txt')
    range_x = range(len(grid[0]))
    range_y = range(len(grid))
    return sum(list([search_location_part_1(grid, x, y, "XMAS") for x in range_x for y in range_y]))

def search_location_part_2(grid, x: int, y: int) -> bool:
    a_in_middle = assert_location(grid, x, y, 'A')
    back_slash_mas = (
            (assert_location(grid, x-1, y+1, 'M') and assert_location(grid, x+1, y-1, 'S')) or
            (assert_location(grid, x-1, y+1, 'S') and assert_location(grid, x+1, y-1, 'M')))
    forward_slash_mas = (
            (assert_location(grid, x-1, y-1, 'M') and assert_location(grid, x+1, y+1, 'S')) or
            (assert_location(grid, x-1, y-1, 'S') and assert_location(grid, x+1, y+1, 'M')))
    return a_in_middle and back_slash_mas and forward_slash_mas

def part2() -> int:
    grid = read_grid('q4.txt')
    xmas_count = 0
    for x in range(len(grid[0])):
        for y in range(len(grid)):
            if search_location_part_2(grid, x, y):
                xmas_count += 1
    return xmas_count

print(part2())