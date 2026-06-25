g = [l.strip() for l in open("q10.txt")]
R = len(g)
C = len(g[0])
s = 0
t = 0
for i in range(R):
    for j in range(C):
        if g[i][j] == "0":
            q = [(i, j)]
            e = {}
            p = 0
            while q:
                y, x = q.pop()
                c = int(g[y][x])
                if c == 9:
                    e[(y, x)] = 1
                    p += 1
                    continue
                for dy, dx in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    ny = y + dy
                    nx = x + dx
                    if ny >= 0 and ny < R and nx >= 0 and nx < C:
                        if int(g[ny][nx]) == c + 1:
                            q.append((ny, nx))
            s += len(e)
            t += p
print(s)
print(t)
