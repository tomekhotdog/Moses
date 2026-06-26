# Low-quality but structured. God function, duplicated p1/p2, magic numbers,
# abbreviated names, raw string indexing, clumsy overlap handling, no types.


def calc(ln, p2):
    # ln = the line, p2 = flag for part 2
    w = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
    res = []
    i = 0
    while i < len(ln):
        c = ln[i]
        if c >= "0" and c <= "9":
            res.append(int(c))
            i = i + 1
        else:
            done = 0
            if p2 == 1:
                j = 0
                while j < 9:
                    word = w[j]
                    # check if word starts here without consuming overlap
                    if ln[i:i + len(word)] == word:
                        res.append(j + 1)
                        # advance only 1 char so eightwo / twone still work
                        i = i + 1
                        done = 1
                        break
                    j = j + 1
            if done == 0:
                i = i + 1
    if len(res) == 0:
        return 0
    return res[0] * 10 + res[len(res) - 1]


def part1(lines):
    s = 0
    for x in lines:
        s = s + calc(x, 0)
    return s


def part2(lines):
    s = 0
    for x in lines:
        s = s + calc(x, 1)
    return s


def run(text):
    lines = text.split("\n")
    lines2 = []
    for q in lines:
        if q != "":
            lines2.append(q)
    print(part1(lines2))
    print(part2(lines2))
