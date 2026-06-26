import sys


def load(fn):
    g = []
    for ln in open(fn):
        ln = ln.strip()
        if ln:
            g.append([int(c) for c in ln])
    return g


def go(g):
    # does everything: counts visible AND finds best scenic score
    R = len(g)
    C = len(g[0])
    vis = 0
    best = 0
    for r in range(R):
        for c in range(C):
            h = g[r][c]
            # ---- visibility, 4 directions duplicated ----
            v = False
            # up
            ok = True
            for i in range(r - 1, -1, -1):
                if g[i][c] >= h:
                    ok = False
                    break
            if ok:
                v = True
            # down
            ok = True
            for i in range(r + 1, R):
                if g[i][c] >= h:
                    ok = False
                    break
            if ok:
                v = True
            # left
            ok = True
            for j in range(c - 1, -1, -1):
                if g[r][j] >= h:
                    ok = False
                    break
            if ok:
                v = True
            # right
            ok = True
            for j in range(c + 1, C):
                if g[r][j] >= h:
                    ok = False
                    break
            if ok:
                v = True
            if v:
                vis += 1
            # ---- scenic score, 4 directions duplicated again ----
            d1 = 0
            for i in range(r - 1, -1, -1):
                d1 += 1
                if g[i][c] >= h:
                    break
            d2 = 0
            for i in range(r + 1, R):
                d2 += 1
                if g[i][c] >= h:
                    break
            d3 = 0
            for j in range(c - 1, -1, -1):
                d3 += 1
                if g[r][j] >= h:
                    break
            d4 = 0
            for j in range(c + 1, C):
                d4 += 1
                if g[r][j] >= h:
                    break
            s = d1 * d2 * d3 * d4
            if s > best:
                best = s
    return vis, best


if __name__ == "__main__":
    g = load(sys.argv[1] if len(sys.argv) > 1 else "input.txt")
    p1, p2 = go(g)
    print(p1)
    print(p2)
