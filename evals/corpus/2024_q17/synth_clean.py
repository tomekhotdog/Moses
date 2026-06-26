"""Advent of Code 2024, Day 17: Chronospatial Computer.

A faithful simulator of the 3-bit virtual machine plus a digit-by-digit
quine search for Part 2.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, replace

# Opcode constants (named instead of magic numbers).
ADV, BXL, BST, JNZ, BXC, OUT, BDV, CDV = range(8)


@dataclass(frozen=True)
class Computer:
    """Immutable register/output state for the virtual machine."""

    a: int
    b: int
    c: int
    output: tuple[int, ...] = ()


@dataclass(frozen=True)
class Program:
    """A parsed program: the initial registers and the instruction stream."""

    a: int
    b: int
    c: int
    code: tuple[int, ...]


def parse(text: str) -> Program:
    """Parse the puzzle input into a :class:`Program`."""
    header, body = text.strip().split("\n\n")
    a, b, c = (int(line.split(":")[1]) for line in header.splitlines())
    code = tuple(int(n) for n in body.split(":")[1].strip().split(","))
    return Program(a=a, b=b, c=c, code=code)


def combo(operand: int, state: Computer) -> int:
    """Resolve a combo operand to its runtime value."""
    if operand <= 3:
        return operand
    return {4: state.a, 5: state.b, 6: state.c}[operand]


def run(program: Program, a: int | None = None) -> tuple[int, ...]:
    """Execute *program* and return the emitted output.

    If *a* is given it overrides the program's initial A register, which is
    what the Part 2 search needs.
    """
    state = Computer(
        a=program.a if a is None else a,
        b=program.b,
        c=program.c,
    )
    code = program.code
    pointer = 0

    while pointer < len(code):
        opcode, operand = code[pointer], code[pointer + 1]

        if opcode == ADV:
            state = replace(state, a=state.a >> combo(operand, state))
        elif opcode == BXL:
            state = replace(state, b=state.b ^ operand)
        elif opcode == BST:
            state = replace(state, b=combo(operand, state) % 8)
        elif opcode == JNZ:
            if state.a != 0:
                pointer = operand
                continue
        elif opcode == BXC:
            state = replace(state, b=state.b ^ state.c)
        elif opcode == OUT:
            state = replace(state, output=state.output + (combo(operand, state) % 8,))
        elif opcode == BDV:
            state = replace(state, b=state.a >> combo(operand, state))
        elif opcode == CDV:
            state = replace(state, c=state.a >> combo(operand, state))

        pointer += 2

    return state.output


def part_one(program: Program) -> str:
    """Return the comma-separated output of the program as given."""
    return ",".join(str(v) for v in run(program))


def part_two(program: Program) -> int:
    """Find the lowest positive A that makes the program output itself.

    Each loop of the program consumes the low 3 bits of A, so the output is
    reconstructed one trailing digit at a time: extend known prefixes of A by
    3 bits and keep those whose output matches the required suffix.
    """
    target = program.code
    candidates = [0]
    for index in range(len(target) - 1, -1, -1):
        suffix = target[index:]
        candidates = [
            (prefix << 3) | digit
            for prefix in candidates
            for digit in range(8)
            if run(program, a=(prefix << 3) | digit) == suffix
        ]
    return min(candidates) if candidates else -1


def main(path: str) -> None:
    program = parse(open(path).read())
    print(part_one(program))
    print(part_two(program))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "q17_example.txt")
