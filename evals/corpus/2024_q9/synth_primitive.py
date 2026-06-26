def go(s):
    d = []
    f = 0
    for i in range(len(s)):
        n = int(s[i])
        if i % 2 == 0:
            for k in range(n):
                d.append(f)
            f = f + 1
        else:
            for k in range(n):
                d.append(-1)
    # part 1
    a = list(d)
    l = 0
    r = len(a) - 1
    while l < r:
        if a[l] != -1:
            l = l + 1
            continue
        if a[r] == -1:
            r = r - 1
            continue
        a[l] = a[r]
        a[r] = -1
        l = l + 1
        r = r - 1
    t1 = 0
    for i in range(len(a)):
        if a[i] != -1:
            t1 = t1 + i * a[i]
    # part 2
    b = list(d)
    m = 0
    for x in b:
        if x > m:
            m = x
    for fid in range(m, -1, -1):
        st = -1
        ln = 0
        for i in range(len(b)):
            if b[i] == fid:
                if st == -1:
                    st = i
                ln = ln + 1
        j = 0
        while j < st:
            if b[j] == -1:
                c = 0
                while j + c < len(b) and b[j + c] == -1:
                    c = c + 1
                if c >= ln:
                    for q in range(ln):
                        b[j + q] = fid
                        b[st + q] = -1
                    break
                else:
                    j = j + c
            else:
                j = j + 1
    t2 = 0
    for i in range(len(b)):
        if b[i] != -1:
            t2 = t2 + i * b[i]
    return t1, t2


if __name__ == "__main__":
    line = open("input.txt").read().strip()
    p1, p2 = go(line)
    print(p1)
    print(p2)
