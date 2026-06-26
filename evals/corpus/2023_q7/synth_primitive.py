from collections import Counter
from functools import cmp_to_key


def t(h, joker):
    # figure out hand type as a number, bigger = better
    c = Counter(h)
    if joker and "J" in c and len(c) > 1:
        j = c["J"]
        del c["J"]
        # dump the jokers onto whatever card we have the most of
        best = sorted(c.items(), key=lambda x: x[1])[-1][0]
        c[best] += j
    v = sorted(c.values(), reverse=True)
    if v[0] == 5:
        return 7
    elif v[0] == 4:
        return 6
    elif v[0] == 3 and v[1] == 2:
        return 5
    elif v[0] == 3:
        return 4
    elif v[0] == 2 and v[1] == 2:
        return 3
    elif v[0] == 2:
        return 2
    else:
        return 1


def cmp1(a, b):
    o = "23456789TJQKA"
    ta = t(a[0], False)
    tb = t(b[0], False)
    if ta != tb:
        return ta - tb
    for i in range(5):
        if a[0][i] != b[0][i]:
            return o.index(a[0][i]) - o.index(b[0][i])
    return 0


def cmp2(a, b):
    o = "J23456789TQKA"
    ta = t(a[0], True)
    tb = t(b[0], True)
    if ta != tb:
        return ta - tb
    for i in range(5):
        if a[0][i] != b[0][i]:
            return o.index(a[0][i]) - o.index(b[0][i])
    return 0


def part1(lines):
    hands = []
    for l in lines:
        p = l.split()
        hands.append((p[0], int(p[1])))
    hands.sort(key=cmp_to_key(cmp1))
    s = 0
    for i in range(len(hands)):
        s += hands[i][1] * (i + 1)
    return s


def part2(lines):
    hands = []
    for l in lines:
        p = l.split()
        hands.append((p[0], int(p[1])))
    hands.sort(key=cmp_to_key(cmp2))
    s = 0
    for i in range(len(hands)):
        s += hands[i][1] * (i + 1)
    return s


if __name__ == "__main__":
    with open("input.txt") as f:
        lines = [x for x in f.read().strip().split("\n")]
    print(part1(lines))
    print(part2(lines))
