import sys


def get_nums(g):
    # returns list of (val, r, c0, c1) tuples
    res = []
    for r in range(len(g)):
        c = 0
        while c < len(g[r]):
            if g[r][c].isdigit():
                c0 = c
                s = ""
                while c < len(g[r]) and g[r][c].isdigit():
                    s = s + g[r][c]
                    c = c + 1
                res.append((int(s), r, c0, c - 1))
            else:
                c = c + 1
    return res


def p1(g):
    nums = get_nums(g)
    t = 0
    for n in nums:
        ok = False
        # check every neighbour of every digit cell (duplicated below in p2)
        for cc in range(n[2], n[3] + 1):
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr == 0 and dc == 0:
                        continue
                    rr = n[1] + dr
                    ccc = cc + dc
                    if rr >= 0 and rr < len(g):
                        if ccc >= 0 and ccc < len(g[rr]):
                            ch = g[rr][ccc]
                            if ch != "." and not ch.isdigit():
                                ok = True
        if ok:
            t = t + n[0]
    return t


def p2(g):
    nums = get_nums(g)
    t = 0
    for r in range(len(g)):
        for c in range(len(g[r])):
            if g[r][c] == "*":
                adj = []
                # for this gear, find numbers whose cells touch it
                # (same neighbour math as p1, duplicated on purpose)
                for n in nums:
                    hit = False
                    for cc in range(n[2], n[3] + 1):
                        for dr in range(-1, 2):
                            for dc in range(-1, 2):
                                if dr == 0 and dc == 0:
                                    continue
                                rr = n[1] + dr
                                ccc = cc + dc
                                if rr == r and ccc == c:
                                    hit = True
                    if hit:
                        adj.append(n[0])
                if len(adj) == 2:
                    t = t + adj[0] * adj[1]
    return t


def main():
    g = [ln for ln in sys.stdin.read().split("\n") if ln != ""]
    print(p1(g))
    print(p2(g))


if __name__ == "__main__":
    main()
