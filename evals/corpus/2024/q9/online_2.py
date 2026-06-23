# Part 1
from itertools import batched

class Solution(TextSolution):
    def part_1(self) -> int:
        assert len(self.input) % 2 == 1
        disk: dict[int, int] = {}
        max_write_location = 0

        for file_id, (file_size, gap_size) in enumerate(
            batched([int(c) for c in self.input + "0"], 2)
        ):
            for pointer in range(max_write_location, max_write_location + file_size):
                disk[pointer] = file_id
            max_write_location += file_size + gap_size

        writer = 0
        reader = max_write_location
        while True:
            while writer in disk:
                writer += 1
            while reader not in disk:
                reader -= 1
            if writer >= reader:
                break
            disk[writer] = disk[reader]
            del disk[reader]

        return sum(
            idx * disk.get(j, 0) for idx, j in enumerate(range(max_write_location))
        )


# Part 2
from dataclasses import dataclass
from typing import Iterable, Literal
from itertools import batched, chain

def parse_ints(l: Iterable[str]) -> list[int]:
    return [int(i) for i in l]

@dataclass
class Item:
    type: Literal["file", "gap"]
    size: int
    id_: int = 0

def expand(i: Item) -> list[int]:
    return [i.id_] * i.size

class Solution(TextSolution):
    def part_2(self) -> int:
        disk: list[Item] = []

        for file_id, (file_size, gap_size) in enumerate(
            batched(parse_ints(self.input + "0"), 2)
        ):
            disk.append(Item("file", id_=file_id, size=file_size))
            disk.append(Item("gap", gap_size))

        reader = len(disk) - 1
        for file_id in range(disk[-2].id_, -1, -1):
            while (f := disk[reader]).type != "file" or f.id_ != file_id:
                reader -= 1

            try:
                writer, g = next(
                    (writer, g)
                    for writer, g in enumerate(disk)
                    if g.type == "gap" and g.size >= f.size
                )
            except StopIteration:
                continue

            if writer > reader:
                continue

            disk[reader] = Item("gap", f.size)
            disk.insert(writer, f)
            g.size -= f.size

        return sum(
            idx * i for idx, i in enumerate(chain.from_iterable(map(expand, disk)))
        )
