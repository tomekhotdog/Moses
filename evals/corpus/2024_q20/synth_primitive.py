import sys


def run(f):
    g = open(f).read().splitlines()
    s = None
    e = None
    for y in range(len(g)):
        for x in range(len(g[y])):
            if g[y][x] == "S":
                s = (y, x)
            if g[y][x] == "E":
                e = (y, x)
    # bfs along the track from start, record distance for every track tile
    d = {}
    d[s] = 0
    q = [s]
    while q:
        c = q.pop(0)
        for dy, dx in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            ny = c[0] + dy
            nx = c[1] + dx
            if ny < 0 or nx < 0 or ny >= len(g) or nx >= len(g[ny]):
                continue
            if g[ny][nx] == "#":
                continue
            if (ny, nx) in d:
                continue
            d[(ny, nx)] = d[c] + 1
            q.append((ny, nx))

    pts = list(d.keys())

    # part 1: cheats up to 2 picoseconds
    c1 = 0
    for i in range(len(pts)):
        for j in range(len(pts)):
            ay, ax = pts[i]
            by, bx = pts[j]
            m = abs(ay - by) + abs(ax - bx)
            if m <= 2 and m >= 1:
                save = d[(by, bx)] - d[(ay, ax)] - m
                if save >= 100:
                    c1 = c1 + 1

    # part 2: cheats up to 20 picoseconds
    c2 = 0
    for i in range(len(pts)):
        for j in range(len(pts)):
            ay, ax = pts[i]
            by, bx = pts[j]
            m = abs(ay - by) + abs(ax - bx)
            if m <= 20 and m >= 1:
                save = d[(by, bx)] - d[(ay, ax)] - m
                if save >= 100:
                    c2 = c2 + 1

    print(c1)
    print(c2)


run(sys.argv[1] if len(sys.argv) > 1 else "q20.txt")
