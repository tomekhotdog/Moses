from collections import deque
import numpy as np

def read_int_grid_from_lines(lines: list[str]) -> np.ndarray:
    int_lines = [[int(char) for char in line.strip()] for line in lines]
    return np.array(int_lines)

def get_reachable_neighbors(topographic_map: np.ndarray, position: tuple[int, int]) -> list:
    row, col = position
    current_value = topographic_map[row, col]
    neighbors = []

    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        new_row, new_col = row + dr, col + dc
        if (0 <= new_row < topographic_map.shape[0] and
            0 <= new_col < topographic_map.shape[1]):
            if topographic_map[new_row, new_col] == current_value + 1:
                neighbors.append((new_row, new_col))

    return neighbors

def search_for_trailends(topographic_map: np.ndarray, start_position: tuple[int, int]) -> int:
    visited = np.zeros_like(topographic_map, dtype=bool)
    visited[start_position] = True
    queue = deque([start_position])
    score = 0

    while queue:
        current_position = queue.pop()
        visited[current_position] = True
        current_value = topographic_map[current_position]

        if current_value == 9:
            score += 1

        for neighbor in get_reachable_neighbors(topographic_map, current_position):
            if not visited[neighbor] and neighbor not in queue:
                queue.append(neighbor)

    return score

def search_for_distinct_trails(topographic_map: np.ndarray, start_position: tuple[int, int]) -> int:
    queue = deque([start_position])
    score = 0

    while queue:
        current_position = queue.pop()
        current_value = topographic_map[current_position]

        if current_value == 9:
            score += 1

        for neighbor in get_reachable_neighbors(topographic_map, current_position):
            queue.append(neighbor)

    return score

def solve_part_1(lines: list[str]) -> int:
    topographic_map = read_int_grid_from_lines(lines)
    sum_of_trailhead_scores = 0

    for row in range(topographic_map.shape[0]):
        for col in range(topographic_map.shape[1]):
            if topographic_map[row, col] == 0:
                trailhead_score = search_for_trailends(topographic_map, (row, col))
                sum_of_trailhead_scores += trailhead_score

    return sum_of_trailhead_scores

def solve_part_2(lines: list[str]) -> int:
    topographic_map = read_int_grid_from_lines(lines)
    sum_of_trailhead_scores = 0

    for row in range(topographic_map.shape[0]):
        for col in range(topographic_map.shape[1]):
            if topographic_map[row, col] == 0:
                trailhead_score = search_for_distinct_trails(topographic_map, (row, col))
                sum_of_trailhead_scores += trailhead_score

    return sum_of_trailhead_scores
