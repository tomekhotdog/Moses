# Source: https://github.com/iyanmv/advent-of-code-2024 (solutions/day24)
# Author: iyanmv. Saved verbatim for AoC corpus (judge context only).
# Part 1 (full simulation) plus Part 2, which here uses HARDCODED swaps found
# by manual graph inspection (networkx graph render). The swaps are specific to
# the author's own puzzle input, not a general solver.
from pathlib import Path
from collections import Counter

import networkx as nx

module_path = Path(__file__).resolve().parent


def parse_input(text):
    regs, opers = text.split("\n\n")

    registers = {}
    for line in regs.splitlines():
        reg, val = line.split(":")
        registers[reg] = int(val)

    operations = []
    for line in opers.splitlines():
        # fmt: off
        x, op, y, _, z, = line.split(" ")
        # fmt: on
        operations.append((op, x, y, z))

    return registers, operations


def apply_op(op, x, y):
    if op == "AND":
        return x and y
    elif op == "OR":
        return x or y
    elif op == "XOR":
        return x ^ y
    else:
        raise ValueError("Unknown op")


def get_result(registers):
    keys = sorted([key for key in registers.keys() if key.startswith("z")])
    result = 0
    for i, key in enumerate(keys):
        result += registers[key] << i
    return result


def part_1(registers, operations):
    pending = operations.copy()
    while len(pending) > 0:
        for instruction in pending:
            op, in1, in2, out = instruction
            if in1 not in registers or in2 not in registers:
                continue
            registers[out] = apply_op(op, registers[in1], registers[in2])
            pending.remove(instruction)
    return get_result(registers)


def modify_operations(operations, swap):
    new_operations = operations.copy()
    for a, b in swap:
        for i, op1 in enumerate(operations):
            if op1[3] == a:
                a = i
                for j, op2 in enumerate(operations):
                    if op2[3] == b:
                        b = j
                        break
                else:
                    continue
                break
        # fmt: off
        new_operations[a] = (operations[a][0], operations[a][1], operations[a][2], operations[b][3])
        new_operations[b] = (operations[b][0], operations[b][1], operations[b][2], operations[a][3])
        # fmt: on
    return new_operations


def generate_graph(operations):
    graph = nx.DiGraph()
    counter = Counter()
    for op in operations:
        op_name = op[0] + f"_{counter[op[0]]}"
        graph.add_edge(op[1], op_name)
        graph.add_edge(op[2], op_name)
        graph.add_edge(op_name, op[3])
        counter[op[0]] += 1
    return graph


def part_2(operations):
    graph = generate_graph(operations)
    # Manual inspection for weird gates
    # TODO: automatize this somehow
    swaps = [("hdt", "z05"), ("z09", "gbf"), ("mht", "jgt"), ("z30", "nbf")]
    new_operations = modify_operations(operations, swaps)
    graph = generate_graph(new_operations)
    solution = []
    for a, b in swaps:
        solution.append(a)
        solution.append(b)

    return ",".join(sorted(solution))


if __name__ == "__main__":
    with open(module_path / "input", "r") as file:
        registers, operations = parse_input(file.read())

    print("Advent of Code 2024 (day 24 - Python)")
    print(f"Solution for part 1: {part_1(dict(registers), operations)}")
    print(f"Solution for part 2: {part_2(operations)}")
