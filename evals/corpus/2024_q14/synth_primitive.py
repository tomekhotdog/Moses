import sys


class RobotSim:
    def __init__(self, path):
        self.data = []
        f = open(path).read().strip().split("\n")
        for line in f:
            parts = line.split(" ")
            p = parts[0][2:].split(",")
            v = parts[1][2:].split(",")
            # store everything as a tuple, position then velocity
            self.data.append((int(p[0]), int(p[1]), int(v[0]), int(v[1])))

    def run(self):
        # part 1: simulate 100 seconds and compute the safety factor
        q1 = 0
        q2 = 0
        q3 = 0
        q4 = 0
        for r in self.data:
            nx = (r[0] + r[2] * 100) % 101
            ny = (r[1] + r[3] * 100) % 103
            if nx == 50 or ny == 51:
                pass
            else:
                if nx < 50:
                    if ny < 51:
                        q1 += 1
                    else:
                        q3 += 1
                else:
                    if ny < 51:
                        q2 += 1
                    else:
                        q4 += 1
        print(q1 * q2 * q3 * q4)

        # part 2: keep stepping until no two robots share a cell (tree heuristic)
        t = 0
        while True:
            t += 1
            seen = set()
            ok = True
            for r in self.data:
                nx = (r[0] + r[2] * t) % 101
                ny = (r[1] + r[3] * t) % 103
                if (nx, ny) in seen:
                    ok = False
                    break
                seen.add((nx, ny))
            if ok:
                print(t)
                break


def main():
    sim = RobotSim(sys.argv[1])
    sim.run()


if __name__ == "__main__":
    main()
