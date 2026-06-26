import sys


class MonkeyMarket:
    def __init__(self, path):
        f = open(path)
        self.data = [int(x) for x in f.read().split()]

    def next(self, n):
        # evolve the secret one step
        n = (n ^ (n * 64)) % 16777216
        n = (n ^ (n // 32)) % 16777216
        n = (n ^ (n * 2048)) % 16777216
        return n

    def part1(self):
        t = 0
        for s in self.data:
            n = s
            for i in range(2000):
                # same three-step evolution as below (kept inline for speed)
                n = (n ^ (n * 64)) % 16777216
                n = (n ^ (n // 32)) % 16777216
                n = (n ^ (n * 2048)) % 16777216
            t = t + n
        return t

    def part2(self):
        m = {}
        for s in self.data:
            n = s
            p = [n % 10]
            for i in range(2000):
                n = (n ^ (n * 64)) % 16777216
                n = (n ^ (n // 32)) % 16777216
                n = (n ^ (n * 2048)) % 16777216
                p.append(n % 10)
            c = []
            for i in range(len(p) - 1):
                c.append(p[i + 1] - p[i])
            seen = {}
            for i in range(len(c) - 3):
                k = (c[i], c[i + 1], c[i + 2], c[i + 3])
                if k in seen:
                    continue
                seen[k] = 1
                if k in m:
                    m[k] = m[k] + p[i + 4]
                else:
                    m[k] = p[i + 4]
        best = 0
        for v in m.values():
            if v > best:
                best = v
        return best


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "q22_example.txt"
    mm = MonkeyMarket(path)
    print(mm.part1())
    print(mm.part2())


if __name__ == "__main__":
    main()
