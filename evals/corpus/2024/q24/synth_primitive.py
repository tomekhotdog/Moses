import sys

def go(f):
    d = open(f).read().split("\n\n")
    w = {}
    for l in d[0].split("\n"):
        if not l.strip():
            continue
        a = l.split(":")
        w[a[0].strip()] = int(a[1].strip())
    g = []
    for l in d[1].split("\n"):
        if not l.strip():
            continue
        p = l.split("->")
        x = p[0].strip().split(" ")
        g.append((x[0], x[1], x[2], p[1].strip()))
    while True:
        done = 1
        for x in g:
            if x[3] not in w and x[0] in w and x[2] in w:
                if x[1] == "AND":
                    w[x[3]] = w[x[0]] & w[x[2]]
                elif x[1] == "OR":
                    w[x[3]] = w[x[0]] | w[x[2]]
                else:
                    w[x[3]] = w[x[0]] ^ w[x[2]]
                done = 0
        if done:
            break
    z = [k for k in w if k[0] == "z"]
    z.sort(reverse=True)
    s = ""
    for k in z:
        s = s + str(w[k])
    return int(s, 2)

print(go(sys.argv[1] if len(sys.argv) > 1 else "q24.txt"))
