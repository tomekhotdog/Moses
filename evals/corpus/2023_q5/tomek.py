from typing import List
from main import read_input


class SeedRange:
    def __init__(self, start: int, length: int):
        self.start = start
        self.end = start + length
        self.length = length

    def __str__(self):
        return f"{self.start} {self.length}"

    def in_range(self, value):
        return self.start <= value < self.start + self.length


class MappingRange:
    def __init__(self, destination_start, source_start, length):
        self.destination_start = destination_start
        self.source_start = source_start
        self.source_end = source_start + length
        self.length = length

    def __str__(self):
        return f"[{self.destination_start}-{self.source_start}-{self.length}]"

    def in_input_range(self, value: int):
        return self.source_start <= value < self.source_start + self.length

    def map(self, value: int):
        return value if not self.in_input_range(value) else self.destination_start + value - self.source_start


class Mapping:
    def __init__(self, source_category, destination_category, ranges: List[MappingRange]):
        self.source_category = source_category
        self.destination_category = destination_category
        self.ranges = sorted(ranges, key=lambda x: x.source_start)

    def __str__(self):
        return f"{self.source_category}->{self.destination_category}"

    def map_value(self, value: int) -> int:
        for mapping_range in self.ranges:
            if mapping_range.in_input_range(value):
                return mapping_range.map(value)
        return value

    def map_range(self, seed_range: SeedRange) -> List[SeedRange]:
        mapped_seed_ranges = []
        current = seed_range
        for mapping in self.ranges:
            # Seed range comes before mapping range.
            if current.end < mapping.source_start:
                mapped_seed_ranges.append(current)
                return mapped_seed_ranges
            # Seed range is intersected by mapping range.
            if current.start < mapping.source_start <= current.end:
                length_before_mapping = mapping.source_start - current.start
                mapped_seed_ranges.append(SeedRange(current.start, length_before_mapping))
                current = SeedRange(mapping.source_start, current.end - mapping.source_start)
            if current.start < mapping.source_end:
                delta = mapping.destination_start - mapping.source_start
                if current.end <= mapping.source_end:
                    mapped_seed_ranges.append(SeedRange(current.start + delta, current.length))
                    return mapped_seed_ranges
                elif current.end > mapping.source_end:
                    mapped_seed_ranges.append(SeedRange(current.start + delta, mapping.source_end - current.start))
                    current = SeedRange(mapping.source_end, current.end - mapping.source_end)
            # Seed range comes after mapping range.
            if current.start > mapping.source_end:
                continue
        if current.length > 0:
            mapped_seed_ranges.append(current)
        return mapped_seed_ranges


class Almanac:
    def __init__(self, mappings: List[Mapping]):
        self.mappings = mappings
        self.mappings_reversed = mappings.copy()
        self.mappings_reversed.reverse()

    def process_seed(self, seed: int) -> int:
        current = seed
        for mapping in self.mappings:
            current = mapping.map_value(current)
        return current

    def process_seed_range(self, seed_range: SeedRange) -> List[SeedRange]:
        seed_ranges = [seed_range]
        for mapping in self.mappings:
            seed_ranges = [mapping.map_range(x) for x in seed_ranges]
            seed_ranges = [item for sublist in seed_ranges for item in sublist]
        return seed_ranges


def parse_seeds_part_1(line: str) -> List[int]:
    return [int(x) for x in line.split(':')[1].strip().split(' ')]


def parse_seeds_part_2(line: str) -> List[SeedRange]:
    elems = line.split(':')[1].strip().split(' ')
    seed_ranges = []
    i = 0
    while i < len(elems):
        seed_ranges.append(SeedRange(int(elems[i]), int(elems[i+1])))
        i += 2
    return seed_ranges


def parse_almanac(lines: List[str]) -> Almanac:
    mappings = []
    mapping_ranges = []
    source = ""
    destination = ""
    for line in lines:
        if 'map' in line:
            elems = line.split(' ')[0].split('-')
            source = elems[0]
            destination = elems[2]
        elif line == '':
            mappings.append(Mapping(source, destination, mapping_ranges))
            mapping_ranges = []
        else:
            items = [int(x) for x in line.split(' ')]
            mapping_ranges.append(MappingRange(items[0], items[1], items[2]))

    return Almanac(mappings)


def parse_input_part_1(filename: str) -> (List[int], Almanac):
    lines = read_input(filename)
    return parse_seeds_part_1(lines[0]), parse_almanac(lines[2:])


def parse_input_part_2(filename: str) -> (List[SeedRange], Almanac):
    lines = read_input(filename)
    return parse_seeds_part_2(lines[0]), parse_almanac(lines[2:])


def part1() -> int:
    (seeds, almanac) = parse_input_part_1('q5.txt')
    return min(list(map(lambda x: almanac.process_seed(x), seeds)))


def part2() -> int:
    (seed_ranges, almanac) = parse_input_part_2('q5.txt')
    mapped_seed_ranges = [almanac.process_seed_range(sr) for sr in seed_ranges]
    mapped_seed_ranges = [sr for sublist in mapped_seed_ranges for sr in sublist]
    return min([seed_range.start for seed_range in mapped_seed_ranges])
