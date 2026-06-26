from main import read_input
from enum import Enum

class Direction(Enum):
    N = 1
    E = 2
    S = 3
    W = 4

    def __str__(self):
        return self.name

    def symbol(self) -> chr:
        symbol_map = {
            Direction.N: '^',
            Direction.E: '>',
            Direction.S: 'v',
            Direction.W: '<'
        }
        return symbol_map[self]

    def rotate_right(self):
        next_dir = {
            Direction.N: Direction.E,
            Direction.E: Direction.S,
            Direction.S: Direction.W,
            Direction.W: Direction.N
        }
        return next_dir[self]

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

class Guard:
    def __init__(self, coordinates: Coordinates, direction: Direction):
        self.coordinates = coordinates
        self.direction = direction

    def __eq__(self, other):
        if isinstance(other, Guard):
            return (self.coordinates == other.coordinates and
                    self.direction == other.direction)
        return False

    def __hash__(self):
        return hash((hash(self.coordinates), hash(self.direction)))

    def __str__(self):
        return f'Location={self.coordinates}. Facing={self.direction}'

    def copy(self):
        return Guard(self.coordinates, self.direction)

class Lab:
    def __init__(self, lab_map: [[]], guard: Guard):
        self.lab_map = lab_map
        self.guard = guard
        self.width = len(lab_map)
        self.height = len(lab_map[0])
        self.guard_start = self.guard.copy()
        self.guard_history = { self.guard }
        self.time_point = 0
        self.in_loop = False

    def outside_map(self, coordinates: Coordinates):
        return (coordinates.X < 0 or coordinates.X >= self.width or
                coordinates.Y < 0 or coordinates.Y >= self.height)

    def move_once(self):
        if self.guard.direction == Direction.N:
            proposed = Coordinates(self.guard.coordinates.X, self.guard.coordinates.Y - 1)
        elif self.guard.direction == Direction.E:
            proposed = Coordinates(self.guard.coordinates.X + 1, self.guard.coordinates.Y)
        elif self.guard.direction == Direction.S:
            proposed = Coordinates(self.guard.coordinates.X, self.guard.coordinates.Y + 1)
        elif self.guard.direction == Direction.W:
            proposed = Coordinates(self.guard.coordinates.X - 1, self.guard.coordinates.Y)
        else:
            raise Exception('Failed to move the guard.')

        remains_in_map = not self.outside_map(proposed)
        if remains_in_map and self.lab_map[proposed.Y][proposed.X] == '#':
            self.guard.direction = self.guard.direction.rotate_right()
        else:
            self.guard.coordinates = proposed

        # Record new guard location.
        if remains_in_map:
            guard_location = self.guard.copy()
            if guard_location in self.guard_history:
                self.in_loop = True
            self.guard_history.add(self.guard.copy())
        self.time_point += 1

    def simulate(self):
        while not self.outside_map(self.guard.coordinates) and not self.in_loop:
            self.move_once()

def parse_direction(symbol: chr) -> Direction:
    symbol_map = {
        '>': Direction.E,
        'v': Direction.S,
        '<': Direction.W,
        '^': Direction.N
    }
    if symbol not in symbol_map:
        raise Exception(f"Failed to parse direction: {symbol}")
    return symbol_map[symbol]

def parse_lab(filename: str) -> Lab:
    raw_input = read_input(filename)
    width = len(raw_input[0])
    height = len(raw_input)
    lab_map = [['.' for _ in range(width)] for _ in range(height)]
    guard = Guard(Coordinates(-1,-1), Direction.N)
    for y in range(height):
        for x in range(width):
            map_symbol = raw_input[y][x]
            # Assume the guard is at this location.
            if map_symbol != '.' and map_symbol != '#':
                guard = Guard(Coordinates(x, y), parse_direction(map_symbol))
                map_symbol = '.'
            lab_map[y][x] = map_symbol
    return Lab(lab_map, guard)

def print_lab(lab: Lab):
    for y in range(len(lab.lab_map)):
        line = ''
        for x in range(len(lab.lab_map[0])):
            map_symbol = lab.lab_map[y][x]
            if lab.guard.coordinates == Coordinates(x, y):
                map_symbol = lab.guard.direction.symbol()
            line += map_symbol
        print(line)

def part1() -> int:
    lab = parse_lab('q6.txt')
    lab.simulate()
    return len(set([guard.coordinates for guard in lab.guard_history]))

def part2() -> int:
    lab = parse_lab('q6.txt')
    hypotheticals_with_loops = 0

    for y in range(lab.height):
        for x in range(lab.width):
            # Cannot place hypothetical obstacle on starting point.
            if Coordinates(x, y) == lab.guard_start.coordinates:
                continue
            original_elem = lab.lab_map[y][x]
            # Obstacle already exists in this location.
            if original_elem == '#':
                continue
            # Simulate hypothetical lab with additional obstacle added.
            hypothetical = Lab(lab.lab_map, lab.guard.copy())
            hypothetical.lab_map[y][x] = '#'
            hypothetical.simulate()
            # Put element back as it was (grim!)
            lab.lab_map[y][x] = original_elem

            if hypothetical.in_loop:
                hypotheticals_with_loops += 1

    return hypotheticals_with_loops

print(part1())
# Brute force approach takes ~5 mins to terminate.
print(part2())