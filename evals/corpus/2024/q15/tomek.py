from main import read_input

def parse_warehouse(filename, scaled_up=False):
    warehouse = []
    instructions = ''
    reached_instructions = False
    for line in read_input(filename):
        if line == '':
            reached_instructions = True
        elif reached_instructions:
            instructions += line
        else:
            warehouse.append(list(line))

    walls = set()
    boxes = set()
    left_boxes = set()
    right_boxes = set()
    robot = 0,0
    height = len(warehouse)
    width = len(warehouse[0])
    for y in range(len(warehouse)):
        for x in range(len(warehouse[0])):
            item = warehouse[y][x]
            if item == '#':
                if scaled_up:
                    walls.add((2 * x, y))
                    walls.add((2 * x + 1, y))
                else:
                    walls.add((x,y))
            if item == 'O':
                if scaled_up:
                    left_boxes.add((2 * x, y))
                    right_boxes.add((2 * x + 1, y))
                else:
                    boxes.add((x,y))
            if item == '@':
                if scaled_up:
                    robot = 2 * x, y
                else:
                    robot = x,y

    warehouse_width = width if not scaled_up else 2 * width
    return Warehouse(walls, boxes, left_boxes, right_boxes, robot, warehouse_width, height), instructions

class Warehouse:
    def __init__(self, walls, boxes, left_boxes, right_boxes, robot, width, height):
        self.walls = walls
        self.boxes = boxes
        self.left_boxes = left_boxes
        self.right_boxes = right_boxes
        self.robot = robot
        self.width = width
        self.height = height

def print_warehouse(warehouse: Warehouse):
    for y in range(warehouse.height):
        line = ''
        for x in range(warehouse.width):
            item = '.'
            if (x,y) == warehouse.robot:
                item = '@'
            elif (x,y) in warehouse.walls:
                item = '#'
            elif (x,y) in warehouse.boxes:
                item = 'O'
            elif (x,y) in warehouse.left_boxes:
                item = '['
            elif (x,y) in warehouse.right_boxes:
                item = ']'
            line += item
        print(line)

def simulate(warehouse, instructions, diagnostic=False):
    if diagnostic:
        print('Initial state:')
        print_warehouse(warehouse)
    for instruction in instructions:
        simulate_instruction(warehouse, instruction)
        if diagnostic:
            print(f'\nMove {instruction}:')
            print_warehouse(warehouse)
    return warehouse

def simulate_instruction(warehouse, instruction):
    if can_move(warehouse, warehouse.robot, instruction):
        move(warehouse, warehouse.robot, instruction)

def can_move(warehouse, item_pos, instruction):
    next_pos = next_position(item_pos, instruction)
    x_next, y_next = next_pos
    if next_pos in warehouse.walls:
        return False
    elif next_pos in warehouse.boxes:
        return can_move(warehouse, next_pos, instruction)
    elif next_pos in warehouse.left_boxes:
        # If moving left side of wide box ([) up/down, need to consider right side (])
        if instruction in ['<', '>']:
            return can_move(warehouse, next_pos, instruction)
        else:
            right_side_pos = x_next + 1, y_next
            return (can_move(warehouse, next_pos, instruction) and
                    can_move(warehouse, right_side_pos, instruction))
    elif next_pos in warehouse.right_boxes:
        # If moving right side of wide box (]) up/down, need to consider left side ([)
        if instruction in ['<', '>']:
            return can_move(warehouse, next_pos, instruction)
        else:
            left_side_pos = x_next - 1, y_next
            return (can_move(warehouse, next_pos, instruction) and
                    can_move(warehouse, left_side_pos, instruction))
    else:
        return True

def next_position(position, instruction):
    x, y = position
    if instruction == '<':
        return x - 1, y
    elif instruction == '>':
        return x + 1, y
    elif instruction == '^':
        return x, y - 1
    elif instruction == 'v':
        return x, y + 1
    else:
        raise Exception(f"Unexpected instruction: {instruction}")

def move(warehouse, item_pos, instruction):
    x, y = item_pos
    next_pos = next_position(item_pos, instruction)

    if item_pos in warehouse.walls:
        raise Exception("Cannot move wall!")

    # Clear up space we're moving into (with call to move()), then move current item.
    elif item_pos in warehouse.boxes:
        move(warehouse, next_pos, instruction)
        warehouse.boxes.remove(item_pos)
        warehouse.boxes.add(next_pos)

    # If moving left side of wide box ([) up/down, need to also move corresponding right side (])
    elif item_pos in warehouse.left_boxes:
        move(warehouse, next_pos, instruction)
        warehouse.left_boxes.remove(item_pos)
        warehouse.left_boxes.add(next_pos)
        if instruction in ['^', 'v']:
            right_side_pos = x + 1, y
            right_side_pos_next = next_position(right_side_pos, instruction)
            move(warehouse, right_side_pos_next, instruction)
            warehouse.right_boxes.remove(right_side_pos)
            warehouse.right_boxes.add(right_side_pos_next)

    # If moving right side of wide box (]) up/down, need to also move corresponding left side ([)
    elif item_pos in warehouse.right_boxes:
        move(warehouse, next_pos, instruction)
        warehouse.right_boxes.remove(item_pos)
        warehouse.right_boxes.add(next_pos)
        if instruction in ['^', 'v']:
            left_side_pos = x - 1, y
            left_side_pos_next = next_position(left_side_pos, instruction)
            move(warehouse, left_side_pos_next, instruction)
            warehouse.left_boxes.remove(left_side_pos)
            warehouse.left_boxes.add(left_side_pos_next)

    elif item_pos == warehouse.robot:
        move(warehouse, next_pos, instruction)
        warehouse.robot = next_pos

def box_gps_coordinates_sum(warehouse, scaled_up):
    if scaled_up:
        return sum([(100 * y) + x for (x, y) in warehouse.left_boxes])
    else:
        return sum([(100 * y) + x for (x, y) in warehouse.boxes])

def part1() -> int:
    warehouse, instructions = parse_warehouse('q15.txt')
    simulate(warehouse, instructions, diagnostic=False)
    return box_gps_coordinates_sum(warehouse, False)

def part2() -> int:
    warehouse, instructions = parse_warehouse('q15.txt', scaled_up=True)
    simulate(warehouse, instructions, diagnostic=False)
    return box_gps_coordinates_sum(warehouse, True)

print(part1())
print(part2())