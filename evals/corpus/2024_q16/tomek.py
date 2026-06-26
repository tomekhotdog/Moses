from main import read_input
from enum import Enum

class Maze:
    def __init__(self, maze, start, end):
        self.maze = maze
        self.start = start
        self.end = end

    def __str__(self):
        return self.maze_to_string() + f'\nS={self.start}' + f'\nE={self.end}'

    def maze_to_string(self):
        return '\n'.join([''.join(row) for row in self.maze])

    def possible_location(self, x_and_y):
        x, y = x_and_y
        return 0 <= x < len(self.maze[0]) and 0 <= y < len(self.maze) and self.maze[y][x] != '#'


class Direction(Enum):
    N = 0
    E = 1
    S = 2
    W = 3

class Position:
    def __init__(self, x, y, direction: Direction):
        self.x = x
        self.y = y
        self.direction = direction

    def __str__(self):
        return f'({self.x}, {self.y}), {self.direction}'

    def __eq__(self, other):
        return (isinstance(other, type(self))
                and (self.x, self.y, self.direction) ==
                    (other.x, other.y, other.direction))

    def __hash__(self):
        return hash((self.x, self.y, self.direction))

class Step:
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.cost = self.calculate_cost()
        if (abs(self.start.x - self.end.x) + abs(self.start.y - self.end.y)) != 1:
            raise Exception("Tried to construct impossible step!")

    def __str__(self):
        return f'[{self.start}] -> [{self.end}]'

    def calculate_cost(self):
        rotations = (self.start.direction.value + self.end.direction.value) % 2
        return 1 + (rotations * 1000)

def parse_maze(filename):
    maze = read_input(filename)
    start, end = None, None
    for y in range(len(maze)):
        for x in range(len(maze[0])):
            if maze[y][x] == 'S':
                start = (x, y)
            elif maze[y][x] == 'E':
                end = (x, y)

    return Maze(maze, start, end)

def visit_maze(maze: Maze):
    # Explore the maze from the start, iteratively calculating the minimum cost to arrive at each location.
    min_position_costs = {}
    prev_tiles = {} # Previous tile along cheapest path (or multiple in case of equal cost options).
    steps_to_evaluate = []

    start_x, start_y = maze.start
    start_position = Position(start_x, start_y, Direction.E)
    min_position_costs[start_position] = 0
    steps_to_evaluate += possible_steps(maze, start_position)

    while len(steps_to_evaluate) > 0:
        step = steps_to_evaluate.pop(0)
        min_position_costs.setdefault(step.end, 1e12)
        start_cost = min_position_costs[step.start]
        proposed_path_cost = start_cost + step.cost
        step_improves_existing = proposed_path_cost < min_position_costs[step.end]
        step_equals_existing = proposed_path_cost == min_position_costs[step.end]

        if step_improves_existing:
            min_position_costs[step.end] = proposed_path_cost
            prev_tiles[step.end] = [step.start]
            for possible_step in possible_steps(maze, step.end):
                subsequent_cum_cost = proposed_path_cost + possible_step.cost
                if possible_step.end not in min_position_costs or subsequent_cum_cost < min_position_costs[possible_step.end]:
                    steps_to_evaluate.append(possible_step)

        if step_equals_existing:
            prev_tiles[step.end].append(step.start)

    return min_position_costs, prev_tiles

def possible_steps(maze: Maze, start: Position):
    start_coordinates = start.x, start.y
    steps = []
    for direction in Direction:
        next_x, next_y = step_in_direction(start_coordinates, direction)
        if maze.possible_location((next_x, next_y)):
            next_position = Position(next_x, next_y, direction)
            steps.append(Step(start, next_position))
    return steps

def step_in_direction(start_coordinates, direction):
    x, y = start_coordinates
    if direction == Direction.N:
        return x, y - 1
    elif direction == Direction.E:
        return x + 1, y
    elif direction == Direction.S:
        return x, y + 1
    elif direction == Direction.W:
        return x - 1, y
    else:
        raise Exception(f'Unexpected direction: {direction}!')

def cost_of_maze_end(all_costs, maze_end):
    x, y = maze_end
    final_positions = [Position(x, y, d) for d in Direction]
    return min([(all_costs[p], p) for p in final_positions if p in all_costs], key=lambda t: t[0])

def tiles_along_best_paths(prev_tiles_map, end):
    best_tiles = set()
    to_visit = [end]
    while len(to_visit) > 0:
        current = to_visit.pop(0)
        best_tiles.add((current.x, current.y))
        if current not in prev_tiles_map:
            continue
        for prev in prev_tiles_map[current]:
            to_visit.append(prev)

    return best_tiles

def part1() -> int:
    maze = parse_maze('q16.txt')
    position_costs, _ = visit_maze(maze)
    return cost_of_maze_end(position_costs, maze.end)[0]

def part2() -> int:
    maze = parse_maze('q16.txt')
    position_costs, prev_tiles = visit_maze(maze)
    _, final_position = cost_of_maze_end(position_costs, maze.end)
    return len(tiles_along_best_paths(prev_tiles, final_position))

print(part1())
print(part2())