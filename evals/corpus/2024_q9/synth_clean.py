"""Advent of Code 2024 Day 9: Disk Fragmenter.

Parses a dense disk map, compacts the disk under two policies, and computes
the resulting filesystem checksum for each.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

FREE = -1  # sentinel file id marking a free block


@dataclass(frozen=True)
class Span:
    """A contiguous run of blocks belonging to one file, in disk order."""

    file_id: int
    start: int
    length: int


def parse_disk_map(dense: str) -> list[int]:
    """Expand a dense disk map into a per-block list of file ids (FREE for gaps)."""
    blocks: list[int] = []
    for position, digit in enumerate(dense):
        count = int(digit)
        is_file = position % 2 == 0
        file_id = position // 2 if is_file else FREE
        blocks.extend([file_id] * count)
    return blocks


def compact_by_block(blocks: list[int]) -> list[int]:
    """Move single blocks from the right into the leftmost gaps (Part 1)."""
    disk = list(blocks)
    left, right = 0, len(disk) - 1
    while left < right:
        if disk[left] != FREE:
            left += 1
        elif disk[right] == FREE:
            right -= 1
        else:
            disk[left], disk[right] = disk[right], FREE
            left += 1
            right -= 1
    return disk


def file_spans(blocks: list[int]) -> list[Span]:
    """Return one Span per file, ordered by increasing start position."""
    spans: list[Span] = []
    index = 0
    while index < len(blocks):
        file_id = blocks[index]
        if file_id == FREE:
            index += 1
            continue
        start = index
        while index < len(blocks) and blocks[index] == file_id:
            index += 1
        spans.append(Span(file_id, start, index - start))
    return spans


def _leftmost_gap(blocks: list[int], length: int, before: int) -> int | None:
    """Index of the leftmost free run of at least `length`, starting before `before`."""
    index = 0
    while index < before:
        if blocks[index] != FREE:
            index += 1
            continue
        run_start = index
        while index < before and blocks[index] == FREE:
            index += 1
        if index - run_start >= length:
            return run_start
    return None


def compact_by_file(blocks: list[int]) -> list[int]:
    """Move whole files (highest id first) into the leftmost fitting gap (Part 2)."""
    disk = list(blocks)
    for span in sorted(file_spans(disk), key=lambda s: s.file_id, reverse=True):
        target = _leftmost_gap(disk, span.length, before=span.start)
        if target is None:
            continue
        for offset in range(span.length):
            disk[target + offset] = span.file_id
            disk[span.start + offset] = FREE
    return disk


def checksum(blocks: list[int]) -> int:
    """Sum of position * file_id over all filled blocks."""
    return sum(position * file_id for position, file_id in enumerate(blocks) if file_id != FREE)


def solve(dense: str) -> tuple[int, int]:
    blocks = parse_disk_map(dense)
    return checksum(compact_by_block(blocks)), checksum(compact_by_file(blocks))


def main() -> None:
    dense = Path("input.txt").read_text().strip()
    part1, part2 = solve(dense)
    print(part1)
    print(part2)


if __name__ == "__main__":
    main()
