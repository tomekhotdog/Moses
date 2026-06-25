import time
import copy


MOVES = {
    '>': (1, 0),
    '<': (-1, 0),
    '^': (0, -1),
    'v': (0, 1)
}


def parse_input(file: str) -> list:
    with open(file, 'r') as f:
        lines = f.readlines()

    map_block = True
    map = []
    moves = []
    for line in lines:
        line = line.strip()
        if map_block:
            if line == '':
                map_block = False
                continue
            map.append(list(line))

            if '@' in line:
                initial_position = (line.index('@'), len(map) - 1)

        else:
            moves += line

    return map, initial_position, moves

def move_entity(entity: str, map: list, position: tuple, move: str) -> tuple:
    delta_x, delta_y = MOVES[move]

    new_x = position[0] + delta_x
    new_y = position[1] + delta_y

    # check if new position is out of bounds
    if new_x < 0 or new_x >= len(map[0]) or new_y < 0 or new_y >= len(map) or map[new_y][new_x] == '#':
        return position

    if map[new_y][new_x] == 'O':
        new_candidate = move_entity('O', map, (new_x, new_y), move)
        if new_candidate == (new_x, new_y):
            return position

    map[new_y][new_x] = entity
    map[position[1]][position[0]] = '.'

    return new_x, new_y

def part_a(file: str)  -> int:
    map, initial_position, moves = parse_input(file)

    # move the player
    current_position = initial_position
    for move in moves:
        current_position = move_entity('@', map, current_position, move)

    # get coordinates of all boxes
    sum_ = 0
    for row in range(len(map)):
        for col in range(len(map[0])):
            if map[row][col] == 'O':
                sum_ += 100 * row + col

    return sum_

def parse_input_part_b(file: str) -> list:
    with open(file, 'r') as f:
        lines = f.readlines()

    map_block = True
    map = []
    moves = []
    for line in lines:
        line = line.strip()
        if map_block:
            if line == '':
                map_block = False
                continue
            row = []
            for char in line:
                if char == '@':
                    row.append('@')
                    row.append('.')
                if char == '#':
                    row.append('#')
                    row.append('#')
                if char == '.':
                    row.append('.')
                    row.append('.')
                if char == 'O':
                    row.append('[')
                    row.append(']')
            map.append(row)

            if '@' in row:
                initial_position = (row.index('@'), len(map) - 1)

        else:
            moves += line

    return map, initial_position, moves

def move_entity_part_b(entity: str, map: list, position: tuple, move: str) -> tuple:
    delta_x, delta_y = MOVES[move]

    new_x = position[0] + delta_x
    new_y = position[1] + delta_y

    # check if new position is out of bounds
    if new_x < 0 or new_x >= len(map[0]) or new_y < 0 or new_y >= len(map) or map[new_y][new_x] == '#':
        return position, True

    block_type = map[new_y][new_x]

    # horizontal movement
    if move in ['>', '<']:
        if block_type == '[':
            new_candidate, flag = move_entity_part_b('[', map, (new_x, new_y), move)
            if flag or new_candidate == (new_x, new_y):
                return position, True
        elif block_type == ']':
            new_candidate, flag = move_entity_part_b(']', map, (new_x, new_y), move)
            if flag or new_candidate == (new_x, new_y):
                return position, True
    else:
    # vertical movement
        if block_type == '[':
            new_candidate_left, flag_left = move_entity_part_b('[', map, (new_x, new_y), move)
            new_candidate_right, flag_right = move_entity_part_b(']', map, (new_x+1, new_y), move)
            if flag_left or flag_right or new_candidate_left == (new_x, new_y) or new_candidate_right == (new_x+1, new_y):
                return position, True
        elif block_type == ']':
            new_candidate_left, flag_left = move_entity_part_b('[', map, (new_x-1, new_y), move)
            new_candidate_right, flag_right = move_entity_part_b(']', map, (new_x, new_y), move)
            if flag_left or flag_right or new_candidate_left == (new_x-1, new_y) or new_candidate_right == (new_x, new_y):
                return position, True

    map[new_y][new_x] = entity
    map[position[1]][position[0]] = '.'

    return (new_x, new_y), False


def part_b(file: str)  -> int:
    map, initial_position, moves = parse_input_part_b(file)

    # move the player
    current_position = initial_position
    prev_map = map
    for move in moves:
        current_map = copy.deepcopy(prev_map)
        current_position, impossible_move = move_entity_part_b('@', current_map, current_position, move)
        if not impossible_move:
            prev_map = current_map

    # get coordinates of all boxes
    sum_ = 0
    for row in range(len(prev_map)):
        for col in range(len(prev_map[0])):
            if prev_map[row][col] == '[':
                sum_ += 100 * row + col

    return sum_

if __name__ == '__main__':

    file = './15/input.txt'

    init_t = time.perf_counter()
    part_a_sol = part_a(file)
    end_t = time.perf_counter()
    elapsed = end_t - init_t
    print(f'\033[32mPart A: {part_a_sol}')
    print(f'Part A: {elapsed * 1e3:.2f} ms\033[0m')

    init_t = time.perf_counter()
    part_b_sol = part_b(file)
    end_t = time.perf_counter()
    elapsed = end_t - init_t
    print(f'\033[34mPart B: {part_b_sol}')
    print(f'Part B: {elapsed * 1e3:.2f} ms\033[0m')
