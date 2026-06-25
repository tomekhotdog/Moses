import os

import re

DAY = 13


def parse(game):
    regex = r'Button \w: X\+(\d+), Y\+(\d+)\nButton \w: X\+(\d+), Y\+(\d+)\nPrize: X=(\d+), Y=(\d+)'
    ax, ay, bx, by, x, y = [int(v) for v in re.findall(regex, game)[0]]
    return ax, bx, ay, by, x, y


def solve(ax, bx, ay, by, x, y, adj):
    x += adj
    y += adj
    det = ax * by - bx * ay
    det_A = x * by - y * bx
    det_B = y * ax - x * ay

    final_a = det_A/det
    final_b = det_B/det

    if final_a != int(final_a) or final_b != int(final_b):
        return 0
    elif final_a < 0 or final_b < 0:
        return 0
    else:
        return 3 * final_a + final_b


def solve_all(data):
    s1= 0
    s2 = 0
    adj = 10_000_000_000_000
    for game in data.split('\n\n'):
        values = parse(game)
        s1 += solve(*values, 0)
        s2 += solve(*values, adj)
    return int(s1), int(s2)


TEST_DATA = '''Button A: X+94, Y+34
Button B: X+22, Y+67
Prize: X=8400, Y=5400

Button A: X+26, Y+66
Button B: X+67, Y+21
Prize: X=12748, Y=12176

Button A: X+17, Y+86
Button B: X+84, Y+37
Prize: X=7870, Y=6450

Button A: X+69, Y+23
Button B: X+27, Y+71
Prize: X=18641, Y=10279'''


print(f'Day {DAY} of Advent of Code!')
print('Testing...')
s1, s2 = solve_all(TEST_DATA)
print(f'Wrong conversion:', s1 == 480)
print(f'Proper conversion:', s2 == 875318608908)

input_path = f"{os.getcwd()}\\{str(DAY).zfill(2)}\\inp"
with open(input_path, mode='r', encoding='utf-8') as inp:
    print('Solution...')
    data = inp.read()
    s1, s2 = solve_all(data)
    print(f'Wrong conversion:', s1)
    print(f'Proper conversion:', s2)
