from main import read_input
from typing import List
from enum import Enum
import math


class Direction(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4


class Forest:
    def __init__(self, grid: List[List[int]]):
        # Tree grid. self.grid[0][0] represents the top left corner.
        self.grid = grid

    def __str__(self):
        string = ""
        for row in self.grid:
            for item in row:
                string += str(item)
            string += '\n'
        return string


def parse_map() -> List[List[int]]:
    return [list(map(lambda tree: int(tree), line)) for line in read_input("q8.txt")]


# Returns a list of booleans. Each element represents a tree from the given tree to the relevant edge.
# The value indicates whether the tree is shorter than the tree in question.
def shorter_trees_in_direction(forest: Forest, row: int, col: int, direction: Direction) -> List[bool]:
    tree_height = forest.grid[row][col]
    match direction:
        case Direction.UP:
            return [forest.grid[i][col] < tree_height for i in range(row-1, -1, -1)]
        case Direction.DOWN:
            return [forest.grid[j][col] < tree_height for j in range(row+1, len(forest.grid), 1)]
        case Direction.LEFT:
            return [forest.grid[row][k] < tree_height for k in range(col-1, -1, -1)]
        case Direction.RIGHT:
            return [forest.grid[row][m] < tree_height for m in range(col+1, len(forest.grid[0]), 1)]


def tree_is_visible_in_direction(forest: Forest, row: int, col: int, direction: Direction) -> bool:
    return all(shorter_trees_in_direction(forest, row, col, direction))


def tree_is_visible(forest: Forest, row: int, col: int) -> bool:
    return any([tree_is_visible_in_direction(forest, row, col, d) for d in Direction])


def count_visible_trees(forest: Forest) -> int:
    visible_trees = 0
    for row in range(len(forest.grid)):
        for col in range(len(forest.grid[0])):
            if tree_is_visible(forest, row, col):
                visible_trees += 1
    return visible_trees


def viewing_distance_in_direction(forest: Forest, row: int, col: int, direction: Direction) -> int:
    shorter_trees = shorter_trees_in_direction(forest, row, col, direction)
    count = 0
    for shorter in shorter_trees:
        if shorter:
            count += 1
        else:
            return count + 1
    return count


def scenic_score(forest: Forest, row: int, col: int) -> int:
    return math.prod([viewing_distance_in_direction(forest, row, col, d) for d in Direction])


def max_scenic_score(forest: Forest) -> int:
    best_score = 0
    for row in range(len(forest.grid)):
        for col in range(len(forest.grid[0])):
            score = scenic_score(forest, row, col)
            best_score = max(best_score, score)
    return best_score


def part1() -> int:
    return count_visible_trees(Forest(parse_map()))


def part2() -> int:
    return max_scenic_score(Forest(parse_map()))
