import sys


def rd(fn):
    f = open(fn)
    d = f.read().split("\n")
    f.close()
    r = []
    for ln in d:
        if ln != "":
            r.append(ln)
    return r


def go(fn):
    g = rd(fn)
    # find empty rows
    er = []
    for i in range(len(g)):
        e = 1
        for j in range(len(g[i])):
            if g[i][j] == "#":
                e = 0
        if e == 1:
            er.append(i)
    # find empty cols
    ec = []
    for j in range(len(g[0])):
        e = 1
        for i in range(len(g)):
            if g[i][j] == "#":
                e = 0
        if e == 1:
            ec.append(j)
    # collect galaxies as raw tuples
    gal = []
    for i in range(len(g)):
        for j in range(len(g[i])):
            if g[i][j] == "#":
                gal.append((i, j))

    # PART 1 (factor 2)
    p1 = 0
    for a in range(len(gal)):
        for b in range(a + 1, len(gal)):
            r1 = gal[a][0]
            c1 = gal[a][1]
            r2 = gal[b][0]
            c2 = gal[b][1]
            lo_r = min(r1, r2)
            hi_r = max(r1, r2)
            lo_c = min(c1, c2)
            hi_c = max(c1, c2)
            d = (hi_r - lo_r) + (hi_c - lo_c)
            for x in er:
                if lo_r < x < hi_r:
                    d = d + 1  # factor 2 means add 1
            for y in ec:
                if lo_c < y < hi_c:
                    d = d + 1
            p1 = p1 + d

    # PART 2 (factor 1000000) -- same thing again, copy pasted
    p2 = 0
    for a in range(len(gal)):
        for b in range(a + 1, len(gal)):
            r1 = gal[a][0]
            c1 = gal[a][1]
            r2 = gal[b][0]
            c2 = gal[b][1]
            lo_r = min(r1, r2)
            hi_r = max(r1, r2)
            lo_c = min(c1, c2)
            hi_c = max(c1, c2)
            d = (hi_r - lo_r) + (hi_c - lo_c)
            for x in er:
                if lo_r < x < hi_r:
                    d = d + 999999  # 1000000 - 1
            for y in ec:
                if lo_c < y < hi_c:
                    d = d + 999999
            p2 = p2 + d

    print(p1)
    print(p2)
    return (p1, p2)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        go(sys.argv[1])
    else:
        go("input.txt")
