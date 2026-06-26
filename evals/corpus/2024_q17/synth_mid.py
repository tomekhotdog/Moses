import sys


def parse(path):
    lines = open(path).read().strip().splitlines()
    a = int(lines[0].split(":")[1])
    b = int(lines[1].split(":")[1])
    c = int(lines[2].split(":")[1])
    program = [int(x) for x in lines[4].split(":")[1].strip().split(",")]
    return a, b, c, program


def execute(a, b, c, program):
    regs = {"a": a, "b": b, "c": c}
    out = []
    ip = 0

    def combo(operand):
        if operand <= 3:
            return operand
        if operand == 4:
            return regs["a"]
        if operand == 5:
            return regs["b"]
        if operand == 6:
            return regs["c"]
        raise ValueError("bad combo operand 7")

    while ip < len(program):
        opcode = program[ip]
        operand = program[ip + 1]

        if opcode == 0:
            regs["a"] = regs["a"] // (2 ** combo(operand))
        elif opcode == 1:
            regs["b"] = regs["b"] ^ operand
        elif opcode == 2:
            regs["b"] = combo(operand) % 8
        elif opcode == 3:
            if regs["a"] != 0:
                ip = operand
                continue
        elif opcode == 4:
            regs["b"] = regs["b"] ^ regs["c"]
        elif opcode == 5:
            out.append(combo(operand) % 8)
        elif opcode == 6:
            regs["b"] = regs["a"] // (2 ** combo(operand))
        elif opcode == 7:
            regs["c"] = regs["a"] // (2 ** combo(operand))

        ip += 2

    return out


def part1(a, b, c, program):
    return ",".join(str(x) for x in execute(a, b, c, program))


def part2(b, c, program):
    # Reconstruct A 3 bits at a time from the last output digit backwards.
    candidates = [0]
    for i in range(len(program)):
        wanted = program[len(program) - 1 - i:]
        new_candidates = []
        for cand in candidates:
            for digit in range(8):
                a = cand * 8 + digit
                if execute(a, b, c, program) == wanted:
                    new_candidates.append(a)
        candidates = new_candidates
    return min(candidates) if candidates else None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "q17_example.txt"
    a, b, c, program = parse(path)
    print(part1(a, b, c, program))
    print(part2(b, c, program))


if __name__ == "__main__":
    main()
