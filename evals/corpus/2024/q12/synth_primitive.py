import sys

f = open(sys.argv[1]) if len(sys.argv) > 1 else open("example3.txt")
g = [l.rstrip("\n") for l in f if l.strip() != ""]
H = len(g)
W = len(g[0])

seen = [[0] * W for _ in range(H)]
p1 = 0
p2 = 0

for i in range(H):
    for j in range(W):
        if seen[i][j]:
            continue
        c = g[i][j]
        st = [(i, j)]
        cells = []
        seen[i][j] = 1
        while st:
            y, x = st.pop()
            cells.append((y, x))
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny = y + dy
                nx = x + dx
                if 0 <= ny < H and 0 <= nx < W and not seen[ny][nx] and g[ny][nx] == c:
                    seen[ny][nx] = 1
                    st.append((ny, nx))
        a = len(cells)
        per = 0
        for y, x in cells:
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny = y + dy
                nx = x + dx
                if not (0 <= ny < H and 0 <= nx < W) or g[ny][nx] != c:
                    per += 1
        p1 += a * per
        s = set(cells)
        co = 0
        for y, x in cells:
            for dy, dx in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                v = (y + dy, x) in s
                h = (y, x + dx) in s
                d = (y + dy, x + dx) in s
                if (not v and not h) or (v and h and not d):
                    co += 1
        p2 += a * co

print(p1)
print(p2)
