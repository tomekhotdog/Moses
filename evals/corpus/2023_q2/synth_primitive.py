import sys


def p1(lines):
    # parse and check possibility all in one go
    s = 0
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        a = ln.split(":")
        gid = int(a[0].split(" ")[1])
        rounds = a[1].split(";")
        ok = True
        for rd in rounds:
            r = 0
            g = 0
            b = 0
            for c in rd.split(","):
                c = c.strip()
                n = int(c.split(" ")[0])
                col = c.split(" ")[1]
                if col == "red":
                    r = n
                elif col == "green":
                    g = n
                elif col == "blue":
                    b = n
            if r > 12 or g > 13 or b > 14:  # 12/13/14 are the bag limits
                ok = False
        if ok:
            s = s + gid
    return s


def p2(lines):
    # basically the same parse again, but compute power instead
    s = 0
    for ln in lines:
        ln = ln.strip()
        if not ln:
            continue
        a = ln.split(":")
        rounds = a[1].split(";")
        mr = 0
        mg = 0
        mb = 0
        for rd in rounds:
            for c in rd.split(","):
                c = c.strip()
                n = int(c.split(" ")[0])
                col = c.split(" ")[1]
                if col == "red" and n > mr:
                    mr = n
                elif col == "green" and n > mg:
                    mg = n
                elif col == "blue" and n > mb:
                    mb = n
        s = s + mr * mg * mb
    return s


if __name__ == "__main__":
    data = open(sys.argv[1] if len(sys.argv) > 1 else "input.txt").readlines()
    print(p1(data))
    print(p2(data))
