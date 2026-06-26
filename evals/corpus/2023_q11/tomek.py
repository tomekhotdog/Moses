from typing import List
from main import read_input


class Image:
    def __init__(self, image: List[str]):
        self.empty_ys = [y for y, row in enumerate(image) if all(x != "#" for x in row)]
        self.empty_xs = [x for x in range(len(image[0])) if all(row[x] != "#" for row in image)]
        self.universes = find_universes(image)

    def __str__(self):
        return f"EmptyXs=[{self.empty_xs}] EmptyYs=[{self.empty_ys}] Universes=[{self.universes}]"


class Universe:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x},{self.y})"

    def __eq__(self, other):
        if isinstance(other, Universe):
            return self.x == other.x and self.y == other.y
        return False

    def __hash__(self):
        return hash(f"{self.x}{self.y}")


class UniversePair:

    def __init__(self, universe1: Universe, universe2: Universe):
        self.universe1 = universe1
        self.universe2 = universe2

    def __str__(self):
        return f"{self.universe1}-{self.universe2}"

    def __eq__(self, other):
        if isinstance(other, UniversePair):
            return (self.universe1 == other.universe1 and self.universe2 == other.universe2) or\
                   (self.universe1 == other.universe2 and self.universe2 == other.universe1)
        return False

    def __hash__(self):
        return hash(self.universe1) + hash(self.universe2)


def manhattan_distance(p: UniversePair, image: Image, empty_space_multiplier: int):
    min_x = min(p.universe1.x, p.universe2.x)
    max_x = max(p.universe1.x, p.universe2.x)
    min_y = min(p.universe1.y, p.universe2.y)
    max_y = max(p.universe1.y, p.universe2.y)

    empty_xs = len([x for x in image.empty_xs if min_x < x < max_x])
    empty_ys = len([y for y in image.empty_ys if min_y < y < max_y])
    observable_manhattan = (max_x - min_x) + (max_y - min_y)

    return observable_manhattan + ((empty_space_multiplier - 1) * (empty_xs + empty_ys))


def find_universes(image: List[str]) -> List[Universe]:
    universes = []
    for y in range(len(image)):
        for x in range(len(image[0])):
            if image[y][x] == '#':
                universes.append(Universe(x, y))
    return universes


def part1() -> int:
    image = Image(read_input('q11.txt'))
    universe_pairs = list(set([UniversePair(u1, u2) for u1 in image.universes for u2 in image.universes if u1 != u2]))
    return sum([manhattan_distance(p, image, 2) for p in universe_pairs])


def part2() -> int:
    image = Image(read_input('q11.txt'))
    universe_pairs = list(set([UniversePair(u1, u2) for u1 in image.universes for u2 in image.universes if u1 != u2]))
    return sum([manhattan_distance(p, image, 1_000_000) for p in universe_pairs])
