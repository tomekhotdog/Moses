# Advent of Code 2023, Day 3 — Gear Ratios
# Source: https://github.com/siddydutta/Advent-of-Code-2023
#   (Day_3_Gear_Ratios/part1.py + part2.py, combined as-found)

# ---------------------------------------------------------------------------
# Part 1
# ---------------------------------------------------------------------------
DELTA = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))

file = open('input.txt')
data = file.read()
file.close()

data = data.strip()
schematic = list(map(list, (map(str.strip, data.split('\n')))))

part_number_indices = []
for n_row, row in enumerate(schematic):
    current_number = []
    current_indices = []
    for n_col, ch in enumerate(row):
        if ch.isdigit():
            current_number.append(ch)
            current_indices.append((n_row, n_col))
        else:
            if current_number:
                part_number = int(''.join(current_number))
                part_number_indices.append((part_number, current_indices))
            current_number = []
            current_indices = []
    # for numbers at the end of the row
    if current_number:
        part_number = int(''.join(current_number))
        part_number_indices.append((part_number, current_indices))

part_numbers_sum = 0
for part_number, indices in part_number_indices:
    added = False
    for n_row, n_col in indices:
        for d_row, d_col in DELTA:
            row = n_row + d_row
            col = n_col + d_col
            if 0 <= row < len(schematic) and 0 <= col < len(schematic[0]):
                if not schematic[row][col].isdigit() and schematic[row][col] != '.':
                    part_numbers_sum += part_number
                    added = True
                    break
        if added:
            break

print(part_numbers_sum)


# ---------------------------------------------------------------------------
# Part 2
# ---------------------------------------------------------------------------
import uuid

indices_map = {}
part_number_map = {}
for n_row, row in enumerate(schematic):
    current_number = []
    current_indices = []
    for n_col, ch in enumerate(row):
        if ch.isdigit():
            current_number.append(ch)
            current_indices.append((n_row, n_col))
        else:
            if current_number:
                part_number = int(''.join(current_number))
                uid = str(uuid.uuid4())
                for index in current_indices:
                    indices_map[index] = uid
                    part_number_map[uid] = part_number
            current_number = []
            current_indices = []
    # for numbers at the end of the row
    if current_number:
        part_number = int(''.join(current_number))
        uid = str(uuid.uuid4())
        for index in current_indices:
            indices_map[index] = uid
            part_number_map[uid] = part_number

gear_ratio_sum = 0
for row in range(len(schematic)):
    for col in range(len(schematic[0])):
        if schematic[row][col] == '*':
            part_number_ids = set()
            for d_row, d_col in DELTA:
                n_row = row + d_row
                n_col = col + d_col
                if 0 <= n_row < len(schematic) and 0 <= n_col < len(schematic[0]):
                    if (n_row, n_col) in indices_map:
                        part_number_ids.add(indices_map[(n_row, n_col)])
            if len(part_number_ids) == 2:
                gear_ratio_sum += part_number_map[part_number_ids.pop()] * part_number_map[part_number_ids.pop()]
print(gear_ratio_sum)
