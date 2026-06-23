f = open("input.txt")
g = []
for l in f:
    g.append(l.strip())

def solve():
    c1 = 0
    c2 = 0
    for i in range(len(g)):
        for j in range(len(g[i])):
            # part 1: check all 8 directions for XMAS
            for di in [-1, 0, 1]:
                for dj in [-1, 0, 1]:
                    if di == 0 and dj == 0:
                        continue
                    s = ""
                    for k in range(4):
                        ni = i + di * k
                        nj = j + dj * k
                        if ni >= 0 and ni < len(g) and nj >= 0 and nj < len(g[i]):
                            s = s + g[ni][nj]
                        else:
                            s = s + "."
                    if s == "XMAS":
                        c1 = c1 + 1
            # part 2: check X-MAS centered here
            if i >= 1 and i < len(g) - 1 and j >= 1 and j < len(g[i]) - 1:
                if g[i][j] == "A":
                    a = g[i-1][j-1]
                    b = g[i+1][j+1]
                    cc = g[i-1][j+1]
                    d = g[i+1][j-1]
                    if (a == "M" and b == "S") or (a == "S" and b == "M"):
                        if (cc == "M" and d == "S") or (cc == "S" and d == "M"):
                            c2 = c2 + 1
    print(c1)
    print(c2)

solve()
