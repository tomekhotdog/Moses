from typing import List
from main import read_input
from enum import Enum


class Colour(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3


string_to_colour_map = {
    'red': Colour.RED,
    'green': Colour.GREEN,
    'blue': Colour.BLUE
}


# Represents the Elf's bag of cubes.
class Bag:
    def __init__(self, red_cubes: int, green_cubes: int, blue_cubes: int):
        self.r = red_cubes
        self.g = green_cubes
        self.b = blue_cubes


# Represents the cubes revealed by the elf in a single round of a game.
class Round:
    def __init__(self, r: int, g: int, b: int):
        self.r = r
        self.g = g
        self.b = b

    def __str__(self):
        return f"[R={self.r},G={self.g},B={self.b}]"

    def compatible_with(self, bag: Bag):
        return self.r <= bag.r and self.g <= bag.g and self.b <= bag.b


class Game:
    def __init__(self, game_id: int, rounds: List[Round]):
        self.game_id = game_id
        self.rounds = rounds

    def __str__(self):
        rounds_string = ','.join(list(map(lambda x: str(x), self.rounds)))
        return f"Id={self.game_id}. Rounds={rounds_string}"

    def compatible_with(self, bag: Bag):
        return all(map(lambda x: x.compatible_with(bag), self.rounds))

    # Defined as the product of the number of each coloured cube that represents
    # the minimal set of cubes compatible with each of the rounds.
    def min_power(self):
        min_red = max(list(map(lambda x: x.r, self.rounds)))
        min_green = max(list(map(lambda x: x.g, self.rounds)))
        min_blue = max(list(map(lambda x: x.b, self.rounds)))
        return min_red * min_green * min_blue


def parse_games(input_string: List[str]) -> List[Game]:
    games = []
    for line in input_string:
        game_elems = line.split(':')
        game_id = int(game_elems[0].split(' ')[1].strip())
        rounds_string = game_elems[1].split(';')
        rounds = []
        for round_string in rounds_string:
            colours = round_string.split(',')
            colour_counts = {Colour.RED: 0, Colour.GREEN: 0, Colour.BLUE: 0}
            for colour_desc in colours:
                elems = colour_desc.strip().split(' ')
                n = int(elems[0].strip())
                colour_string = elems[1].strip()
                assert colour_string in string_to_colour_map, f"Unexpected colour! {colour_string}"
                colour_counts[string_to_colour_map[colour_string]] = n
            rounds.append(Round(colour_counts[Colour.RED], colour_counts[Colour.GREEN], colour_counts[Colour.BLUE]))
        games.append(Game(game_id, rounds))
    return games


def part1() -> int:
    games = parse_games(read_input('q2.txt'))
    compatible_games = list(filter(lambda x: x.compatible_with(Bag(12, 13, 14)), games))
    return sum(list(map(lambda x: x.game_id, compatible_games)))


def part2() -> int:
    games = parse_games(read_input('q2.txt'))
    return sum(list(map(lambda x: x.min_power(), games)))