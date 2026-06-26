import sys


def ld(fn):
    f = open(fn)
    d = []
    for ln in f.readlines():
        ln = ln.strip()
        if ln == "":
            continue
        p = ln.split(" ")
        d.append((p[0], p[1]))
    f.close()
    return d


def p1(d):
    # part 1: 2nd col is the shape we play
    t = 0
    for r in d:
        a = r[0]
        b = r[1]
        # shape score
        if b == "X":
            t = t + 1
        elif b == "Y":
            t = t + 2
        elif b == "Z":
            t = t + 3
        # outcome score
        if (a == "A" and b == "X") or (a == "B" and b == "Y") or (a == "C" and b == "Z"):
            t = t + 3
        elif (a == "A" and b == "Y") or (a == "B" and b == "Z") or (a == "C" and b == "X"):
            t = t + 6
        else:
            t = t + 0
    return t


def p2(d):
    # part 2: 2nd col is the outcome we must reach
    t = 0
    for r in d:
        a = r[0]
        o = r[1]
        # figure out the shape, then re-score it (copy of p1 logic, mostly)
        if o == "X":
            t = t + 0
            if a == "A":
                b = "Z"
            elif a == "B":
                b = "X"
            else:
                b = "Y"
        elif o == "Y":
            t = t + 3
            if a == "A":
                b = "X"
            elif a == "B":
                b = "Y"
            else:
                b = "Z"
        else:
            t = t + 6
            if a == "A":
                b = "Y"
            elif a == "B":
                b = "Z"
            else:
                b = "X"
        if b == "X":
            t = t + 1
        elif b == "Y":
            t = t + 2
        elif b == "Z":
            t = t + 3
    return t


if __name__ == "__main__":
    fn = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    d = ld(fn)
    print(p1(d))
    print(p2(d))
