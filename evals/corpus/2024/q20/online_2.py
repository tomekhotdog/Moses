import os

import heapq
from collections import defaultdict

DAY = 20

START = 'S'
END = 'E'
WALL = '#'
FLOOR = '.'

UP, RIGHT, DOWN, LEFT = ((-1, 0), (0, 1), (1, 0), (0, -1))

DIRECTIONS = [UP, RIGHT, DOWN, LEFT]


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
    path = [start]
    pq = []
    heapq.heapify(pq)
    heapq.heappush(pq, (0, start))

    while pq:
        _, current_vertex = heapq.heappop(pq)
        visited.add(current_vertex)

        neighbors = []
        for direction in DIRECTIONS:
            i, j = current_vertex
            di, dj = direction
            neighbor = (i+di, j+dj)
            if neighbor in grid and grid[neighbor] != WALL:
                neighbors.append(neighbor)

        for neighbor_coords in neighbors:
            if neighbor_coords in visited:
                continue

            old_cost = distances[neighbor_coords]
            new_cost = distances[current_vertex] + 1

            if new_cost < old_cost:
                heapq.heappush(pq, (new_cost, neighbor_coords))
                distances[neighbor_coords] = new_cost
                path.append(neighbor_coords)
    return distances, path


def manhattan(this, other):
    return abs(this[0] - other[0]) + abs(this[1] - other[1])


def look_around(grid, vertex, distance):
    i, j = vertex
    for di in range(i-distance-1, i+distance+1):
        for dj in range(j-distance-1, j+distance+1):
            if (di, dj) in grid and \
                grid[(di, dj)] != WALL and \
                    manhattan(vertex, (di, dj)) <= distance:
                yield (di, dj)


def count_cheats(grid, start, end, hop_dist, minimum_delta):
    from_start, path_from_start = dijkstra(grid, start)
    from_end, _ = dijkstra(grid, end)
    best = from_start[end]
    cheats = defaultdict(int)
    for point in path_from_start:
        for candidate_hop in look_around(grid, point, hop_dist):
            new_dist = from_start[point] + manhattan(point, candidate_hop) + from_end[candidate_hop]
            delta = best - new_dist
            if delta >= minimum_delta:
                cheats[delta] += 1
    return cheats


TEST_DATA = '''###############
#...#...#.....#
#.#.#.#.#.###.#
#S#...#.#.#...#
#######.#.#.###
#######.#.#...#
#######.#.###.#
###..E#...#...#
###.#######.###
#...###...#...#
#.#####.#.###.#
#.#...#.#.#...#
#.#.#.#.#.#.###
#...#...#...###
###############'''


print(f'Day {DAY} of Advent of Code!')
print('Testing...')
grid, start, end = parse(TEST_DATA)
print('Good 20-picosecond cheats:', sum(count_cheats(grid, start, end, 20, 50).values()) == 285)

input_path = f"{os.getcwd()}\\{str(DAY).zfill(2)}\\inp"
with open(input_path, mode='r', encoding='utf-8') as inp:
    print('Solution...')
    data = inp.read()
    grid, start, end = parse(data)
    print('Good 2-picosecond cheats:', sum(count_cheats(grid, start, end, 2, 100).values()))
    print('Good 20-picosecond cheats:', sum(count_cheats(grid, start, end, 20, 100).values()))
