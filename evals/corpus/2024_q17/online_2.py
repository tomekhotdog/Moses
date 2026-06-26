# Source: https://github.com/mattcl/aoc2024-py (aoc/day17.py)
"""17: Chronospatial Computer"""
import aoc.util


class Solver(aoc.util.Solver):
    def __init__(self, input: str):
        super(Solver, self).__init__(input)

        parts = input.strip().split("\n\n")

        self.a = int(parts[0].replace("Register A: ", "").split("\n")[0])
        self.program = list(map(int, parts[1].replace("Program: ", "").split(",")))

        #   for my input,
        #   0 bst 4  b = a & 0b111
        #   2 bxl 3  b = b ^ 3
        #   4 cdv 5  c = a >> b
        #   6 bxc 1  b = b ^ c
        #   8 bxl 3  b = b ^ 3
        #  10 adv 3  a = a >> 3
        #  12 out 5  out b & 0b111
        #  14 jnz 0  goto 0 if a != 0
        #
        # i've been told that the position of the second bxl varies a bit
        #
        # this is the example expected locations from my input
        # expected = [2, 4, 1, v1, 7, 5, 4, v2, 1, v3, 0, 3, 5, 5, 3, 0];

        self.v1 = self.program[3]

        # find the second bxl
        for ip in range(4, len(self.program), 2):
            if self.program[ip] == 1:
                self.v3 = self.program[ip + 1]
                break

    def part_one(self) -> str:
        out = []

        a = self.a

        while a != 0:
            out.append(str(transpiled(a, self.v1, self.v3)))
            a >>= 3

        return ",".join(out)

    def part_two(self) -> int:
        cur = []
        cur.append(0)

        for wanted in reversed(self.program):
            next = []
            for p in cur:
                for i in range(8):
                    a = (p << 3) + i
                    if transpiled(a, self.v1, self.v3) == wanted:
                        next.append(a)

            cur = next

        cur.sort()

        for c in cur:
            digit = 0
            a = c

            while a > 0 and digit < len(self.program):
                digit += 1
                a >>= 3

            if digit == len(self.program):
                return c

        return 0


def transpiled(a, v1, v3) -> int:
    b = (a & 0b111) ^ v1
    return ((b ^ (a >> b)) ^ v3) & 0b111
