"""AoC 2023 Day 5 — If You Give A Seed A Fertilizer.

Models the almanac as a chain of mappings over half-open integer intervals.
Part 1 maps point values; Part 2 maps whole intervals by splitting them at
every mapping boundary, so the huge seed ranges never need enumeration.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass(frozen=True)
class Interval:
    """A half-open interval [start, stop)."""

    start: int
    stop: int

    def __bool__(self) -> bool:
        return self.start < self.stop

    def shifted(self, offset: int) -> "Interval":
        return Interval(self.start + offset, self.stop + offset)


@dataclass(frozen=True)
class RangeRule:
    """One `dest_start src_start length` line: maps a source interval by an offset."""

    source: Interval
    offset: int

    @classmethod
    def parse(cls, line: str) -> "RangeRule":
        dest_start, source_start, length = (int(n) for n in line.split())
        return cls(Interval(source_start, source_start + length), dest_start - source_start)

    def apply_point(self, value: int) -> int | None:
        if self.source.start <= value < self.source.stop:
            return value + self.offset
        return None


@dataclass(frozen=True)
class Mapping:
    """One category-to-category map: a set of rules; unmatched values pass through."""

    rules: tuple[RangeRule, ...]

    @classmethod
    def parse(cls, block: str) -> "Mapping":
        _header, *rows = block.strip().splitlines()
        return cls(tuple(RangeRule.parse(row) for row in rows))

    def map_point(self, value: int) -> int:
        for rule in self.rules:
            mapped = rule.apply_point(value)
            if mapped is not None:
                return mapped
        return value

    def map_interval(self, interval: Interval) -> list[Interval]:
        """Split `interval` against every rule; mapped pieces shift, gaps pass through."""
        mapped: list[Interval] = []
        pending = [interval]
        for rule in self.rules:
            unmatched: list[Interval] = []
            for piece in pending:
                overlap = Interval(
                    max(piece.start, rule.source.start),
                    min(piece.stop, rule.source.stop),
                )
                if overlap:
                    mapped.append(overlap.shifted(rule.offset))
                    left = Interval(piece.start, overlap.start)
                    right = Interval(overlap.stop, piece.stop)
                    if left:
                        unmatched.append(left)
                    if right:
                        unmatched.append(right)
                else:
                    unmatched.append(piece)
            pending = unmatched
        return mapped + pending


@dataclass(frozen=True)
class Almanac:
    seeds: tuple[int, ...]
    mappings: tuple[Mapping, ...]

    @classmethod
    def parse(cls, text: str) -> "Almanac":
        seed_block, *map_blocks = text.strip().split("\n\n")
        seeds = tuple(int(n) for n in seed_block.split(":")[1].split())
        return cls(seeds, tuple(Mapping.parse(block) for block in map_blocks))

    def locate_point(self, seed: int) -> int:
        value = seed
        for mapping in self.mappings:
            value = mapping.map_point(value)
        return value

    def locate_intervals(self, intervals: Iterable[Interval]) -> list[Interval]:
        current = list(intervals)
        for mapping in self.mappings:
            current = [out for iv in current for out in mapping.map_interval(iv)]
        return current

    def seed_intervals(self) -> Iterator[Interval]:
        it = iter(self.seeds)
        for start, length in zip(it, it):
            yield Interval(start, start + length)


def part_1(almanac: Almanac) -> int:
    return min(almanac.locate_point(seed) for seed in almanac.seeds)


def part_2(almanac: Almanac) -> int:
    located = almanac.locate_intervals(almanac.seed_intervals())
    return min(iv.start for iv in located)


def main() -> None:
    with open("input.txt", encoding="utf-8") as handle:
        almanac = Almanac.parse(handle.read())
    print(part_1(almanac))
    print(part_2(almanac))


if __name__ == "__main__":
    main()
