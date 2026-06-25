import sys
from itertools import permutations

numpad = {
    "7": (0, 0), "8": (1, 0), "9": (2, 0),
    "4": (0, 1), "5": (1, 1), "6": (2, 1),
    "1": (0, 2), "2": (1, 2), "3": (2, 2),
    "0": (1, 3), "A": (2, 3),
}
dirpad = {
    "^": (1, 0), "A": (2, 0),
    "<": (0, 1), "v": (1, 1), ">": (2, 1),
}


def get_moves(start, end, gap):
    # build all permutations of the required moves, keep the ones avoiding gap
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy
    moves = []
    moves += [">"] * dx if dx > 0 else ["<"] * -dx
    moves += ["v"] * dy if dy > 0 else ["^"] * -dy
    result = []
    for perm in set(permutations(moves)):
        x, y = sx, sy
        ok = True
        for m in perm:
            if m == "<":
                x -= 1
            elif m == ">":
                x += 1
            elif m == "^":
                y -= 1
            elif m == "v":
                y += 1
            if (x, y) == gap:
                ok = False
                break
        if ok:
            result.append("".join(perm) + "A")
    return result if result else ["A"]


def expand(seq, pad, gap):
    # expand a sequence one keypad level down, returning shortest expansion
    cur = "A"
    out = ""
    for ch in seq:
        options = get_moves(pad[cur], pad[ch], gap)
        out += min(options, key=len)
        cur = ch
    return out


def shortest(code):
    s = expand(code, numpad, (0, 3))
    s = expand(s, dirpad, (0, 0))
    s = expand(s, dirpad, (0, 0))
    return len(s)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "example.txt"
    total = 0
    for line in open(path):
        code = line.strip()
        if not code:
            continue
        num = int("".join(c for c in code if c.isdigit()))
        total += shortest(code) * num
    print(total)


main()
