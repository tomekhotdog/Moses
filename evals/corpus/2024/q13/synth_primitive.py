import sys


class ClawSolver:
    def __init__(self, path):
        self.path = path
        self.machines = []

    def load(self):
        data = open(self.path).read()
        for blk in data.split("\n\n"):
            lines = blk.strip().split("\n")
            if len(lines) < 3:
                continue
            # Button A: X+94, Y+34
            a = lines[0].split(":")[1].split(",")
            ax = int(a[0].split("+")[1])
            ay = int(a[1].split("+")[1])
            b = lines[1].split(":")[1].split(",")
            bx = int(b[0].split("+")[1])
            by = int(b[1].split("+")[1])
            p = lines[2].split(":")[1].split(",")
            px = int(p[0].split("=")[1])
            py = int(p[1].split("=")[1])
            # store everything as a flat dict, no real type
            self.machines.append({"ax": ax, "ay": ay, "bx": bx,
                                  "by": by, "px": px, "py": py})

    def run(self):
        # one big function that does both parts, lots of branching
        part1 = 0
        part2 = 0
        for m in self.machines:
            ax = m["ax"]
            ay = m["ay"]
            bx = m["bx"]
            by = m["by"]
            det = ax * by - ay * bx
            if det != 0:
                # part 1
                px = m["px"]
                py = m["py"]
                na = px * by - py * bx
                nb = ax * py - ay * px
                if na % det == 0 and nb % det == 0:
                    i = na // det
                    j = nb // det
                    if i >= 0:
                        if j >= 0:
                            part1 += 3 * i + j
                # part 2 (basically the same thing again but with offset)
                px2 = m["px"] + 10000000000000
                py2 = m["py"] + 10000000000000
                na2 = px2 * by - py2 * bx
                nb2 = ax * py2 - ay * px2
                if na2 % det == 0 and nb2 % det == 0:
                    i2 = na2 // det
                    j2 = nb2 // det
                    if i2 >= 0:
                        if j2 >= 0:
                            part2 += 3 * i2 + j2
        return part1, part2


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "q13_example.txt"
    s = ClawSolver(path)
    s.load()
    p1, p2 = s.run()
    print(p1)
    print(p2)


if __name__ == "__main__":
    main()
