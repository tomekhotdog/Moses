import sys


def run(fname, p2):
    # read all the monkeys
    data = open(fname).read().split("\n\n")
    items = {}   # monkey -> list of items
    ops = {}     # monkey -> operation string
    divs = {}    # monkey -> divisor
    t = {}       # monkey -> target if true
    f = {}       # monkey -> target if false
    cnt = {}     # monkey -> inspection count
    i = 0
    for blk in data:
        ls = blk.strip().split("\n")
        items[i] = [int(x) for x in ls[1].split(":")[1].split(",")]
        ops[i] = ls[2].split("=")[1].strip()
        divs[i] = int(ls[3].split()[-1])
        t[i] = int(ls[4].split()[-1])
        f[i] = int(ls[5].split()[-1])
        cnt[i] = 0
        i = i + 1

    # the lcm for part 2 (all divisors are prime so just multiply them)
    m = 1
    for k in divs:
        m = m * divs[k]

    rounds = 10000 if p2 else 20
    for r in range(rounds):
        for k in range(len(items)):
            for old in items[k]:
                cnt[k] = cnt[k] + 1
                new = eval(ops[k])   # uses 'old'
                if not p2:
                    new = new // 3
                else:
                    new = new % m
                if new % divs[k] == 0:
                    items[t[k]].append(new)
                else:
                    items[f[k]].append(new)
            items[k] = []

    # monkey business = product of two highest counts
    c = sorted(cnt.values())
    return c[-1] * c[-2]


def part1(fname):
    return run(fname, False)


def part2(fname):
    return run(fname, True)


if __name__ == "__main__":
    fn = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    print(part1(fn))
    print(part2(fn))
