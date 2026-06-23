from main import read_input_string
from typing import List

class FileBlock:
    def __init__(self, file_id: int, file_length: int, empty: bool):
        self.file_id = file_id
        self.file_length = file_length
        self.empty = empty

    def __str__(self):
        return '.' if self.empty else f'{str(self.file_id)[0]}'

# Expand dense format e.g.
# 2333133121414131402 -> 00...111...2...333.44.5555.6666.777.888899
def unpack(dense: str) -> List[FileBlock]:
    file_index = 0
    file_id = 0
    free_space_index = 1
    expanded = []
    while file_index < len(dense):
        file_length = int(dense[file_index])
        for i in range(file_length):
            expanded.append(FileBlock(file_id, file_length,False))
        if free_space_index < len(dense):
            for j in range(int(dense[free_space_index])):
                expanded.append(FileBlock(0, 1,True))
        file_index += 2
        file_id += 1
        free_space_index += 2
    return expanded

# Compact expanded format e.g.
# 0..111....22222
# 02.111....2222.
# 022111....222..
# 0221112...22...
# 02211122..2....
# 022111222......
def compact(expanded: List[FileBlock]) -> List[FileBlock]:
    final_elem_index = len(expanded) - 1
    next_free_index = 0
    while final_elem_index > 0:
        while not expanded[next_free_index].empty:
            next_free_index += 1
        if final_elem_index <= next_free_index:
            break
        expanded[next_free_index] = expanded[final_elem_index]
        expanded[final_elem_index] = FileBlock(0, 1, True)
        final_elem_index -= 1
    return expanded

# Compact expanded format with file fragmentation.
# 00...111...2...333.44.5555.6666.777.888899
# 0099.111...2...333.44.5555.6666.777.8888..
# 0099.1117772...333.44.5555.6666.....8888..
# 0099.111777244.333....5555.6666.....8888..
# 00992111777.44.333....5555.6666.....8888..
def compact_contiguous(expanded: List[FileBlock]) -> List[FileBlock]:
    length = len(expanded)
    elem_index = length - 1

    while elem_index > 0:
        # Identify the next file (descending file_id order).
        while expanded[elem_index].empty and elem_index > 0:
            elem_index -= 1
        elem_length = expanded[elem_index].file_length
        # Attempt to find space for it to be moved.
        next_free_start_index = 0
        while next_free_start_index < elem_index:
            while not expanded[next_free_start_index].empty and next_free_start_index < elem_index:
                next_free_start_index += 1
            # No space found for this element.
            if next_free_start_index >= elem_index:
                break
            next_free_end_index = next_free_start_index
            while expanded[next_free_end_index].empty and next_free_end_index < elem_index:
                next_free_end_index += 1
            free_block_size = next_free_end_index - next_free_start_index
            # Entire block can fit into free slot.
            if free_block_size >= elem_length:
                for i in range(elem_length):
                    expanded[next_free_start_index + i] = expanded[elem_index - i]
                    expanded[elem_index - i] = FileBlock(0, 1, True)
                break
            # Otherwise attempt to find another free space for block.
            next_free_start_index += 1
        # Attempt to move next file.
        elem_index -= 1

    return expanded

def checksum(compacted: List[chr]) -> int:
    total = 0
    for i in range(len(compacted)):
        elem_value = int(compacted[i].file_id) if not compacted[i].empty else 0
        total += elem_value * i
    return total

def part1() -> int:
    dense = read_input_string('q9.txt')
    print(dense)
    expanded = unpack(dense)
    print(''.join([str(elem) for elem in expanded]))
    compacted = compact(expanded)
    print(''.join([str(elem) for elem in compacted]))
    return checksum(compacted)

def part2() -> int:
    dense = read_input_string('q9.txt')
    expanded = unpack(dense)
    compacted = compact_contiguous(expanded)
    return checksum(compacted)


print(part1())
# Execution for part takes ~2mins. Should model free space and files explicitly for more scalable approach.
print(part2())