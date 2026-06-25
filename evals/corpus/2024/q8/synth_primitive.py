import sys

def go(f):
    g = [l.rstrip("\n") for l in open(f) if l.strip() != ""]
    h = len(g)
    w = len(g[0])
    d = {}
    for y in range(h):
        for x in range(w):
            c = g[y][x]
            if c != ".":
                if c not in d:
                    d[c] = []
                d[c].append((y, x))
    s1 = set()
    s2 = set()
    for c in d:
        p = d[c]
        for i in range(len(p)):
            for j in range(len(p)):
                if i == j:
                    continue
                ay, ax = p[i]
                by, bx = p[j]
                dy = by - ay
                dx = bx - ax
                ny = by + dy
                nx = bx + dx
                if 0 <= ny < h and 0 <= nx < w:
                    s1.add((ny, nx))
                k = 0
                while True:
                    ty = ay + k * dy
                    tx = ax + k * dx
                    if 0 <= ty < h and 0 <= tx < w:
                        s2.add((ty, tx))
                        k += 1
                    else:
                        break
    return len(s1), len(s2)

if __name__ == "__main__":
    a, b = go(sys.argv[1] if len(sys.argv) > 1 else "q8.txt")
    print(a)
    print(b)
