from typing import List
from main import read_input
from functools import reduce
import re


class Part:
    def __init__(self, value: int, locations: List[int]):
        self.value = value
        self.locations = locations

    def __str__(self):
        return f"{self.value} [{self.locations}]"

    def is_adjacent(self, grid_width: int, target_index: int):
        deltas = [-grid_width-1, -grid_width, -grid_width+1, -1, 1, grid_width-1, grid_width, grid_width+1]
        return any(map(lambda location: any(map(lambda delta: location+delta == target_index, deltas)), self.locations))


# Assuming we have a grid of fixed width, check whether an element of the grid (represented as a single string) is
# "adjacent" to a symbol by checking the characters at positions around the element in question.
# For example, the '5' is adjacent to the '$'.
#  ..$..
#  ..5..
#  .....
def adjacent_to_a_symbol(index: int, string: str, row_length: int, symbols: set[str]) -> bool:
    # Representing the positions around the item in question.
    index_deltas = [-row_length-1, -row_length, -row_length+1, -1, 1, row_length-1, row_length, row_length+1]
    for delta in index_deltas:
        index_to_check = index + delta
        if index_to_check < 0 or index_to_check > len(string)-1:
            continue
        if string[index_to_check] in symbols:
            return True
    return False


def extract_part_numbers(string: str, line_length: int) -> List[Part]:
    symbols_pattern = r'[^0-9\.]'
    symbols = set(list(re.findall(symbols_pattern, string)))

    part_numbers = []
    current_number = []
    current_locations = []
    current_adjacency = []

    for index, item in enumerate(string):
        if item.isdigit():
            current_number.append(item)
            current_adjacency.append(adjacent_to_a_symbol(index, string, line_length, symbols))
            current_locations.append(index)
        else:
            if len(current_number) > 0 and any(current_adjacency):
                part_number_value = int(str("".join(current_number)))
                part_numbers.append(Part(part_number_value, current_locations))
            current_number = []
            current_locations = []
            current_adjacency = []

    return part_numbers


def find_indexes(string: str, char_to_find: str) -> List[int]:
    return [index for index, item in enumerate(string) if item == char_to_find]


def calculate_gear_ratio(grid_width: int, gear_index: int, parts: List[Part]):
    adjacent_parts = list(filter(lambda x: x.is_adjacent(grid_width, gear_index), parts))
    # Gear-ratio is only well defined in the case of two adjacent parts.
    if len(adjacent_parts) == 2:
        return reduce(lambda x, y: x.raw_value * y.raw_value, adjacent_parts)
    return 0


def part1() -> int:
    lines = read_input('q3.txt')
    grid_width = len(lines[0])
    parts = extract_part_numbers("".join(lines), grid_width)
    return sum([part.value for part in parts])


def part2() -> int:
    lines = read_input('q3.txt')
    grid_width = len(lines[0])
    string = "".join(lines)
    parts = extract_part_numbers(string, grid_width)
    gear_locations = find_indexes(string, '*')
    return sum([calculate_gear_ratio(grid_width, location, parts) for location in gear_locations])