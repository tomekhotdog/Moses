import os

import heapq
from collections import defaultdict

DAY = 16

START = 'S'
END = 'E'
WALL = '#'
FLOOR = '.'

WALK_COST = 1
TURN_COST = 1000

UP, RIGHT, DOWN, LEFT = ((-1, 0), (0, 1), (1, 0), (0, -1))

DIRECTIONS = [UP, RIGHT, DOWN, LEFT]

TURNS = {UP: (LEFT, RIGHT), DOWN: (LEFT, RIGHT), RIGHT: (UP, DOWN), LEFT: (UP, DOWN)}


def parse(data):
    grid = {}
    start = (-1, -1)
    end = (-1, -1)
    for i, row in enumerate(data.splitlines()):
        for j, c in enumerate(row):
            grid[(i, j)] = c
            if c == START:
                start = (i, j)
            elif c == END:
                end = (i, j)
    return grid, start, end


def dijkstra(grid, start):
    distances = {vertex: float('inf') for vertex in grid if grid[vertex] != WALL}
    distances[start] = 0
    visited = set()

    pq = []
    heapq.heapify(pq)
    heapq.heappush(pq, (0, start, RIGHT))

    while pq:
        _, current_vertex, current_direction = heapq.heappop(pq)
        visited.add(current_vertex)

        neighbors = []
        for direction in DIRECTIONS:
            i, j = current_vertex
            di, dj = direction
            neighbor = ((i+di, j+dj), direction)
            if neighbor[0] in grid and grid[neighbor[0]] != WALL:
                neighbors.append(neighbor)

        for neighbor_coords, neighbor_direction in neighbors:
            if neighbor_coords in visited:
                continue
            if neighbor_direction != current_direction:
                distance = TURN_COST + WALK_COST
            else:
                distance = WALK_COST

            old_cost = distances[neighbor_coords]
            new_cost = distances[current_vertex] + distance

            if new_cost < old_cost:
                heapq.heappush(pq, (new_cost, neighbor_coords, neighbor_direction))
                distances[neighbor_coords] = new_cost
    return distances


def dijkstra2(grid, start):
    visited = defaultdict(lambda: float('inf'))
    seats = set()
    best_cost = float('inf')
    path = set([start])

    Q = []
    heapq.heapify(Q)
    heapq.heappush(Q, (0, start, RIGHT, path))

    while Q:
        current_cost, current_vertex, current_direction, path = heapq.heappop(Q)

        if current_cost > visited[(current_vertex, current_direction)] or current_cost > best_cost:
            continue
        else:
            visited[(current_vertex, current_direction)] = current_cost

        if grid[current_vertex] == END:
            if current_cost < best_cost:
                best_cost = current_cost
                seats = path
            elif current_cost == best_cost:
                seats.update(path)
            continue

        di, dj = current_direction
        i, j = current_vertex
        next_move = (i+di, j+dj)

        if grid[next_move] != WALL:
            new_path = path.copy()
            new_path.add(next_move)
            heapq.heappush(Q, (current_cost+WALK_COST, next_move, current_direction, new_path))

        left = TURNS[current_direction][0]
        right = TURNS[current_direction][1]

        heapq.heappush(Q, (current_cost+TURN_COST, current_vertex, left, path.copy()))
        heapq.heappush(Q, (current_cost+TURN_COST, current_vertex, right, path.copy()))

    return len(seats)


TEST_DATA = '''#################
#...#...#...#..E#
#.#.#.#.#.#.#.#.#
#.#.#.#...#...#.#
#.#.#.#.###.#.#.#
#...#.#.#.....#.#
#.#.#.#.#.#####.#
#.#...#.#.#.....#
#.#.#####.#.###.#
#.#.#.......#...#
#.#.###.#####.###
#.#.#...#.....#.#
#.#.#.#####.###.#
#.#.#.........#.#
#.#.#.#########.#
#S#.............#
#################'''


grid, start, end = parse(TEST_DATA)
print(f'Day {DAY} of Advent of Code!')
print('Testing...')
print('Shortest path:', dijkstra(grid, start)[end] == 11048)
print('How many seats:', dijkstra2(grid, start) == 64)

input_path = f"{os.getcwd()}\\{str(DAY).zfill(2)}\\inp"
with open(input_path, mode='r', encoding='utf-8') as inp:
    print('Solution...')
    data = inp.read()
    grid, start, end = parse(data)
    print('Shortest path:', dijkstra(grid, start)[end])
    print('Part 2 may take a while...')
    print('How many seats:', dijkstra2(grid, start))
