import sys

d = open(sys.argv[1] if len(sys.argv) > 1 else "input.txt").read()
a, b = d.split("\n\n")
g = [list(r) for r in a.split("\n")]
m = b.replace("\n", "")

D = {"^": (-1, 0), "v": (1, 0), "<": (0, -1), ">": (0, 1)}

r = c = 0
for i in range(len(g)):
    for j in range(len(g[i])):
        if g[i][j] == "@":
            r, c = i, j
            g[i][j] = "."

for x in m:
    dr, dc = D[x]
    nr, nc = r + dr, c + dc
    k = 1
    while g[r + dr * k][c + dc * k] == "O":
        k += 1
    e = g[r + dr * k][c + dc * k]
    if e == "#":
        continue
    if k == 1:
        r, c = nr, nc
    else:
        g[r + dr * k][c + dc * k] = "O"
        g[nr][nc] = "."
        r, c = nr, nc

s = 0
for i in range(len(g)):
    for j in range(len(g[i])):
        if g[i][j] == "O":
            s += 100 * i + j
print(s)

g2 = []
for r2 in a.split("\n"):
    nr2 = []
    for ch in r2:
        if ch == "#":
            nr2 += ["#", "#"]
        elif ch == "O":
            nr2 += ["[", "]"]
        elif ch == ".":
            nr2 += [".", "."]
        else:
            nr2 += ["@", "."]
    g2.append(nr2)

r = c = 0
for i in range(len(g2)):
    for j in range(len(g2[i])):
        if g2[i][j] == "@":
            r, c = i, j
            g2[i][j] = "."

for x in m:
    dr, dc = D[x]
    if dc != 0:
        k = 1
        while g2[r][c + dc * k] in "[]":
            k += 1
        if g2[r][c + dc * k] == "#":
            continue
        for t in range(c + dc * k, c, -dc):
            g2[r][t] = g2[r][t - dc]
        g2[r][c] = "."
        c = c + dc
    else:
        fr = [(r + dr, c)]
        seen = set()
        ok = True
        q = [(r + dr, c)]
        cells = set()
        while q:
            cr, cc = q.pop()
            if (cr, cc) in seen:
                continue
            seen.add((cr, cc))
            v = g2[cr][cc]
            if v == "#":
                ok = False
                break
            if v == "[":
                cells.add((cr, cc))
                cells.add((cr, cc + 1))
                q.append((cr + dr, cc))
                q.append((cr + dr, cc + 1))
            elif v == "]":
                cells.add((cr, cc))
                cells.add((cr, cc - 1))
                q.append((cr + dr, cc))
                q.append((cr + dr, cc - 1))
        if not ok:
            continue
        ordered = sorted(cells, key=lambda p: p[0], reverse=(dr > 0))
        vals = {}
        for p in cells:
            vals[p] = g2[p[0]][p[1]]
        for p in cells:
            g2[p[0]][p[1]] = "."
        for p in ordered:
            g2[p[0] + dr][p[1]] = vals[p]
        r = r + dr

s2 = 0
for i in range(len(g2)):
    for j in range(len(g2[i])):
        if g2[i][j] == "[":
            s2 += 100 * i + j
print(s2)
