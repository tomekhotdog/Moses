import heapq

def go():
    g = [list(l) for l in open("input.txt").read().splitlines()]
    s = None
    e = None
    for y in range(len(g)):
        for x in range(len(g[0])):
            if g[y][x] == "S":
                s = (x, y)
            if g[y][x] == "E":
                e = (x, y)
    # state is x, y, dx, dy  (start facing east)
    h = [(0, s[0], s[1], 1, 0)]
    d = {}
    p = {}
    best = None
    while h:
        c, x, y, dx, dy = heapq.heappop(h)
        if (x, y, dx, dy) in d and d[(x, y, dx, dy)] < c:
            continue
        d[(x, y, dx, dy)] = c
        if (x, y) == e:
            if best is None:
                best = c
        # forward
        nx = x + dx
        ny = y + dy
        if 0 <= ny < len(g) and 0 <= nx < len(g[0]) and g[ny][nx] != "#":
            nc = c + 1
            k = (nx, ny, dx, dy)
            if k not in d or nc < d[k]:
                d[k] = nc
                p.setdefault(k, [])
                p[k] = [(x, y, dx, dy)]
                heapq.heappush(h, (nc, nx, ny, dx, dy))
            elif nc == d[k]:
                p.setdefault(k, [])
                p[k].append((x, y, dx, dy))
        # turn left
        k1 = (x, y, dy, -dx)
        if k1 not in d or c + 1000 < d[k1]:
            d[k1] = c + 1000
            p[k1] = [(x, y, dx, dy)]
            heapq.heappush(h, (c + 1000, x, y, dy, -dx))
        elif c + 1000 == d[k1]:
            p.setdefault(k1, [])
            p[k1].append((x, y, dx, dy))
        # turn right
        k2 = (x, y, -dy, dx)
        if k2 not in d or c + 1000 < d[k2]:
            d[k2] = c + 1000
            p[k2] = [(x, y, dx, dy)]
            heapq.heappush(h, (c + 1000, x, y, -dy, dx))
        elif c + 1000 == d[k2]:
            p.setdefault(k2, [])
            p[k2].append((x, y, dx, dy))

    # part 1
    p1 = min(d[(e[0], e[1], a, b)] for a, b in [(1, 0), (-1, 0), (0, 1), (0, -1)] if (e[0], e[1], a, b) in d)
    print(p1)
    # part 2 walk back
    seen = set()
    st = [(e[0], e[1], a, b) for a, b in [(1, 0), (-1, 0), (0, 1), (0, -1)] if (e[0], e[1], a, b) in d and d[(e[0], e[1], a, b)] == p1]
    tiles = set()
    while st:
        cur = st.pop()
        if cur in seen:
            continue
        seen.add(cur)
        tiles.add((cur[0], cur[1]))
        for pr in p.get(cur, []):
            st.append(pr)
    print(len(tiles))

go()
