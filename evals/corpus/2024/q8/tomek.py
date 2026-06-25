from main import read_input
from typing import List
from itertools import combinations

class Coordinates:
    def __init__(self, x: int, y: int):
        self.X = x
        self.Y = y

    def __eq__(self, other):
        if isinstance(other, Coordinates):
            return self.X == other.X and self.Y == other.Y
        return False

    def __hash__(self):
        return hash((self.X, self.Y))

    def __str__(self):
        return f'({self.X},{self.Y})'

    def copy(self):
        return Coordinates(self.X, self.Y)

class Antenna:
    def __init__(self, coordinates: Coordinates, identifier: chr):
        self.coordinates = coordinates
        self.identifier = identifier

    def __str__(self):
        return f'{self.identifier} {self.coordinates}'

def parse_grid(filename: str) -> [[]]:
    raw_input = read_input(filename)
    width = len(raw_input[0])
    height = len(raw_input)
    grid = [['.' for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            grid[y][x] = raw_input[y][x]
    return grid

def identify_antennas(grid: [[]]) -> List[Antenna]:
    antennas = []
    for y in range(len(grid)):
        for x in range(len(grid[0])):
            if grid[y][x] != '.':
                antennas.append(Antenna(Coordinates(x, y), grid[y][x]))
    return antennas

def within_grid(grid: [[]], coordinates: Coordinates) -> bool:
    return 0 <= coordinates.Y < len(grid) and 0 <= coordinates.X < len(grid[0])

def identify_antinodes_for_pair(grid: [[]], a1: Antenna, a2: Antenna, resonance_enabled: bool) -> List[Coordinates]:
    delta_x = a2.coordinates.X - a1.coordinates.X
    delta_y = a2.coordinates.Y - a1.coordinates.Y
    if not resonance_enabled:
        # Apply the delta vector once in each direction.
        antinode_1 = Coordinates(a1.coordinates.X - delta_x, a1.coordinates.Y - delta_y)
        antinode_2 = Coordinates(a2.coordinates.X + delta_x, a2.coordinates.Y + delta_y)
        return [antinode_1, antinode_2]
    else:
        # Apply the delta vector n times in both directions until we reach each of grid.
        antinodes = []
        antinode_dir_1 = a1.coordinates
        resonance = 0
        while within_grid(grid, antinode_dir_1):
            antinodes.append(antinode_dir_1)
            antinode_dir_1 = Coordinates(a1.coordinates.X - (resonance * delta_x), a1.coordinates.Y - (resonance * delta_y))
            resonance += 1

        antinode_dir_2 = a2.coordinates
        resonance = 0
        while within_grid(grid, antinode_dir_2):
            antinodes.append(antinode_dir_2)
            antinode_dir_2 = Coordinates(a2.coordinates.X + (resonance * delta_x), a2.coordinates.Y + (resonance * delta_y))
            resonance += 1
    return antinodes

def identify_antinodes(grid: [[]], antennas: List[Antenna], resonance_enabled: bool) -> List[Coordinates]:
    antinodes = []
    unique = list(set([x.identifier for x in antennas]))
    for identifier in unique:
        same_freq = [x for x in antennas if x.identifier == identifier]
        if len(same_freq) == 1:
            raise Exception(f"Only found one antenna for identifier: {identifier}.")
        pairs = list(combinations(same_freq, 2))
        for pair in pairs:
            a1, a2 = pair
            antinodes_for_pair = identify_antinodes_for_pair(grid, a1, a2, resonance_enabled)
            antinodes += antinodes_for_pair
    return antinodes

def print_grid(grid: [[]]):
    for y in range(len(grid)):
        line = ''
        for x in range(len(grid[0])):
            line += grid[y][x]
        print(line)

def part1() -> int:
    grid = parse_grid('q8.txt')
    antennas = identify_antennas(grid)
    antinodes = identify_antinodes(grid, antennas, False)
    return len(list(set(filter(lambda x: within_grid(grid, x), antinodes))))

def part2() -> int:
    grid = parse_grid('q8.txt')
    antennas = identify_antennas(grid)
    antinodes = identify_antinodes(grid, antennas, True)
    return len(list(set(filter(lambda x: within_grid(grid, x), antinodes))))

print(part1())
print(part2())