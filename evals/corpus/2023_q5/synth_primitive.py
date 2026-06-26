# Low quality but structured: god function, abbreviated names, duplicated
# map-walking logic, magic numbers, raw tuples/lists for ranges, no types.


def prs(txt):
    b = txt.split("\n\n")
    sd = [int(x) for x in b[0][6:].split()]
    # build maps as lists of [dst, src, ln]
    mps = []
    for blk in b[1:]:
        ls = blk.split("\n")
        rr = []
        for l in ls[1:]:
            if l.strip() == "":
                continue
            p = l.split()
            rr.append([int(p[0]), int(p[1]), int(p[2])])
        mps.append(rr)
    return sd, mps


def doit(txt):
    sd, mps = prs(txt)

    # part 1 - walk each seed through 7 maps
    res1 = []
    for s in sd:
        v = s
        for m in mps:
            for r in m:
                if v >= r[1] and v < r[1] + r[2]:
                    v = r[0] + v - r[1]
                    break
            else:
                v = v
        res1.append(v)
    p1 = min(res1)

    # part 2 - seeds are pairs, walk ranges through 7 maps
    rngs = []
    i = 0
    while i < len(sd):
        rngs.append((sd[i], sd[i] + sd[i + 1]))
        i = i + 2

    cur = rngs
    for m in mps:
        nxt = []
        for rg in cur:
            todo = [rg]
            while len(todo) > 0:
                a, z = todo.pop()
                hit = 0
                for r in m:
                    ss = r[1]
                    se = r[1] + r[2]
                    o1 = max(a, ss)
                    o2 = min(z, se)
                    if o1 < o2:
                        # mapped piece
                        d = r[0] - r[1]
                        nxt.append((o1 + d, o2 + d))
                        # left leftover
                        if a < o1:
                            todo.append((a, o1))
                        # right leftover
                        if o2 < z:
                            todo.append((o2, z))
                        hit = 1
                        break
                if hit == 0:
                    nxt.append((a, z))
        cur = nxt
    p2 = min([x[0] for x in cur])

    return p1, p2


if __name__ == "__main__":
    with open("input.txt") as f:
        data = f.read()
    a, b = doit(data)
    print(a)
    print(b)
