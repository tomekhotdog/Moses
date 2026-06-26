from main import read_input

class Machine:
    """
    Machine settings defined as follows
    Button A: X + p1, Y + p3
    Button B: X + p2, Y + p4
    Target: X = Tx, Y = Ty
    """
    def __init__(self, p1, p2, p3, p4, tx, ty):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.tx = tx
        self.ty = ty

    def solve(self):
        b = (self.ty - (self.p3 * self.tx / self.p1)) / (self.p4 - (self.p3 * self.p2 / self.p1))
        a = (self.tx - (self.p2 * b)) / self.p1
        return a, b

    def check(self, a, b):
        return ((a * self.p1) + (b * self.p2) == self.tx) and ((a * self.p3) + (b * self.p4) == self.ty)

    # Returns the token cost of beating the machine if possible, otherwise returns 0.
    def win_cost(self):
        a, b = self.solve()
        return (3 * round(a)) + round(b) if self.check(round(a), round(b)) else 0

    def adjust_targets(self, delta):
        self.tx += delta
        self.ty += delta

def parse_machines(filename):
    lines = read_input(filename)
    machines = []
    for i in range(int(len(lines)/4)+1):
        button_a_str = lines[i*4]
        button_a_elems = button_a_str.split(':')[1].split(',')
        p1 = int(button_a_elems[0].strip().split('+')[1].strip())
        p3 = int(button_a_elems[1].strip().split('+')[1].strip())
        button_b_str = lines[(i*4)+1]
        button_b_elems = button_b_str.split(':')[1].split(',')
        p2 = int(button_b_elems[0].strip().split('+')[1].strip())
        p4 = int(button_b_elems[1].strip().split('+')[1].strip())
        prize_str = lines[(i*4)+2]
        prize_elems = prize_str.split(':')[1].strip().split(',')
        tx = int(prize_elems[0].strip().split('=')[1].strip())
        ty = int(prize_elems[1].strip().split('=')[1].strip())
        machines.append(Machine(p1, p2, p3, p4, tx, ty))
    return machines

def part1() -> int:
    machines = parse_machines('q13.txt')
    return sum([m.win_cost() for m in machines])

def part2() -> int:
    machines = parse_machines('q13.txt')
    adjustment = 10000000000000
    list(map(lambda m: m.adjust_targets(adjustment), machines))
    return sum([m.win_cost() for m in machines])


print(part1())
print(part2())