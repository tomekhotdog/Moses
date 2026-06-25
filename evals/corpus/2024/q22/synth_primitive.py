import sys

f = open(sys.argv[1] if len(sys.argv) > 1 else "q22_example.txt")
d = [int(x) for x in f.read().split()]

t = 0
for s in d:
    n = s
    for i in range(2000):
        n = (n ^ (n * 64)) % 16777216
        n = (n ^ (n // 32)) % 16777216
        n = (n ^ (n * 2048)) % 16777216
    t = t + n
print(t)

m = {}
for s in d:
    n = s
    p = [n % 10]
    for i in range(2000):
        n = (n ^ (n * 64)) % 16777216
        n = (n ^ (n // 32)) % 16777216
        n = (n ^ (n * 2048)) % 16777216
        p.append(n % 10)
    c = []
    for i in range(len(p) - 1):
        c.append(p[i + 1] - p[i])
    seen = {}
    for i in range(len(c) - 3):
        k = (c[i], c[i + 1], c[i + 2], c[i + 3])
        if k in seen:
            continue
        seen[k] = 1
        if k in m:
            m[k] = m[k] + p[i + 4]
        else:
            m[k] = p[i + 4]
print(max(m.values()))
