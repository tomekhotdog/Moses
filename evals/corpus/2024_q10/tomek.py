from main import read_input

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

def parse_topographic_map(filename: str) -> [[]]:
    raw_input = read_input(filename)
    width = len(raw_input[0])
    height = len(raw_input)
    topographic_map = [[0 for _ in range(width)] for _ in range(height)]
    for y in range(height):
        for x in range(width):
            if raw_input[y][x] == '.':
                topographic_map[y][x] = 999
            else:
                topographic_map[y][x] = int(raw_input[y][x])
    return topographic_map

def print_topographic_map(topographic_map: [[]]):
    for y in range(len(topographic_map)):
        line = ''
        for x in range(len(topographic_map[0])):
            value = topographic_map[y][x]
            visualisation = f"{value}" if 0 <= value <= 9 else '.'
            line += visualisation
        print(line)

# Defined to be locations with zero elevation.
def find_trailheads(topographic: [[]]):
    trailheads = []
    for y in range(len(topographic)):
        for x in range(len(topographic[0])):
            if topographic[y][x] == 0:
                trailheads.append(Coordinates(x, y))
    return trailheads

def in_bounds(topographic: [[]], location: Coordinates):
    return 0 <= location.X < len(topographic[0]) and 0 <= location.Y < len(topographic)

def find_hiking_trails(topographic: [[]], trailhead: Coordinates, distinct: bool) -> [[Coordinates]]:
    trails = [[trailhead]]
    finished_trails = []
    visited = { trailhead }
    while any(trails):
        updated = []
        for trail in trails:
            latest = trail[-1]
            candidates = [
                Coordinates(latest.X + 1, latest.Y),
                Coordinates(latest.X - 1, latest.Y),
                Coordinates(latest.X, latest.Y + 1),
                Coordinates(latest.X, latest.Y - 1)
            ]

            # Check whether next candidate has already been visited to satisfy trail distinctness.
            distinct_trail = lambda c: not c in visited
            possible_next = lambda c: in_bounds(topographic, c) and topographic[c.Y][c.X] == (topographic[latest.Y][latest.X] + 1)
            accept_candidate = lambda c: possible_next(c) and distinct_trail(c) if distinct else possible_next(c)

            # Find next possible trail positions.
            accepted = list(filter(accept_candidate, candidates))

            if any(accepted):
                for a in accepted:
                    # Add extended trail to updated list.
                    extended = trail.copy()
                    extended.append(a)
                    updated.append(extended)
                    visited.add(a)
            else:
                finished_trails.append(trail)
        trails = updated

    # Hiking trails must start at 0 and end at 9
    hiking_trails = list(filter(lambda x: len(x) == 10, finished_trails))
    return hiking_trails

def solve(filename: str, distinct_trails, print_map: bool):
    topographic = parse_topographic_map(filename)
    if print_map:
        print_topographic_map(topographic)
    trailheads = find_trailheads(topographic)
    return sum(map(lambda x: len(find_hiking_trails(topographic, x, distinct_trails)), trailheads))

def part1() -> int:
    return solve('q10.txt', True, False)

def part2() -> int:
    return solve('q10.txt', False, False)

print(part1())
print(part2())