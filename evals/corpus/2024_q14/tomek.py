from main import read_input
import math
import statistics

class Robot:
    def __init__(self, start_x, start_y, velocity_x, velocity_y):
        self.start_x = start_x
        self.start_y = start_y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y

    def position_at_t(self, t, grid_width, grid_height):
        x = (self.start_x + (t * self.velocity_x)) % grid_width
        y = (self.start_y + (t * self.velocity_y)) % grid_height
        return x,y

    def __str__(self):
        return f"p={self.start_x},{self.start_y} v={self.velocity_x},{self.velocity_y}"

def print_positions(positions, width, height):
    counts = {}
    for pos in positions:
        if pos in counts:
            counts[pos] += 1
        else:
            counts[pos] = 1
    for y in range(height):
        for x in range(width):
            print(int(counts[(x,y)]) if (x,y) in counts else '.', end='')
        print()

def parse_robots(filename):
    robots = []
    for line in read_input(filename):
        pos_elems = line.split(' ')[0].split('=')[1]
        vel_elems = line.split(' ')[1].split('=')[1]
        start_x = int(pos_elems.split(',')[0])
        start_y = int(pos_elems.split(',')[1])
        v_x = int(vel_elems.split(',')[0])
        v_y = int(vel_elems.split(',')[1])
        robots.append(Robot(start_x, start_y, v_x, v_y))
    return robots

def robot_positions_at_t(robots: [Robot], t, grid_width, grid_height):
    return [robot.position_at_t(t, grid_width, grid_height) for robot in robots]

def quadrant_counts(positions, grid_width, grid_height, x_quadrants, y_quadrants, exclude_on_border=False):
    counts = {}
    for pos in positions:
        x,y = pos
        x_quadrant_width = (grid_width - 1) / x_quadrants
        y_quadrant_height = (grid_height-1) / y_quadrants
        if exclude_on_border:
            on_x_borderline = 0 < x < (grid_width - 1) and x % x_quadrant_width == 0
            on_y_borderline = 0 < y < (grid_height - 1) and y % y_quadrant_height == 0
            if on_x_borderline or on_y_borderline:
                continue

        x_quadrant_index = int(max(0, x-1) / x_quadrant_width)
        y_quadrant_index = int(max(0, y-1) / y_quadrant_height)
        quadrant_pos = (x_quadrant_index, y_quadrant_index)
        if quadrant_pos in counts:
            counts[quadrant_pos] += 1
        else:
            counts[quadrant_pos] = 1

    return counts

def part1() -> int:
    robots = parse_robots('q14.txt')
    width, height = 101, 103
    positions = robot_positions_at_t(robots, 100, width, height)
    counts = quadrant_counts(positions, width, height, 2, 2, exclude_on_border=True)
    return math.prod([count for count in counts.values()])

def part2() -> int:
    robots = parse_robots('q14.txt')
    width, height = 101, 103
    # Idea: robot positions at easter-egg time will exhibit maximum variance of quadrant counts (least random).
    var_at_t = []
    # Assume easter-egg appears in first 10_000 time points, pick the one with max variance.
    for t in range(10_000):
        if t % 1000 == 0:
            print(f"Simulating t={t}")
        positions = robot_positions_at_t(robots, t, width, height)
        counts = quadrant_counts(positions, width, height, 10, 10)
        var = statistics.variance(counts.values())
        var_at_t.append((t, var))

    t_at_max_var = max(var_at_t, key=lambda x: x[1])[0]
    positions_at_max_var = robot_positions_at_t(robots, t_at_max_var, width, height)
    print_positions(positions_at_max_var, width, height)
    return t_at_max_var

print(part1())
print(part2())