import sys


class GardenSolver:
    def __init__(self, path):
        f = open(path)
        self.g = [l.rstrip("\n") for l in f if l.strip() != ""]
        self.h = len(self.g)
        self.w = len(self.g[0])
        self.seen = [[0] * self.w for _ in range(self.h)]

    def fld(self, r, c):
        # flood fill region starting at r,c
        ch = self.g[r][c]
        st = [(r, c)]
        self.seen[r][c] = 1
        cells = []
        while st:
            y, x = st.pop()
            cells.append((y, x))
            for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                ny = y + dy
                nx = x + dx
                if ny >= 0 and ny < self.h and nx >= 0 and nx < self.w:
                    if self.seen[ny][nx] == 0 and self.g[ny][nx] == ch:
                        self.seen[ny][nx] = 1
                        st.append((ny, nx))
        return cells

    def run(self):
        p1 = 0
        p2 = 0
        for i in range(self.h):
            for j in range(self.w):
                if self.seen[i][j] == 1:
                    continue
                ch = self.g[i][j]
                cells = self.fld(i, j)
                a = len(cells)
                # perimeter for part 1
                per = 0
                for y, x in cells:
                    for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        ny = y + dy
                        nx = x + dx
                        if ny < 0 or ny >= self.h or nx < 0 or nx >= self.w:
                            per = per + 1
                        else:
                            if self.g[ny][nx] != ch:
                                per = per + 1
                p1 = p1 + a * per
                # corner count for part 2
                s = set(cells)
                co = 0
                for y, x in cells:
                    for dy, dx in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                        v = (y + dy, x) in s
                        hh = (y, x + dx) in s
                        d = (y + dy, x + dx) in s
                        if v == False and hh == False:
                            co = co + 1
                        else:
                            if v == True and hh == True and d == False:
                                co = co + 1
                p2 = p2 + a * co
        return p1, p2


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "example3.txt"
    gs = GardenSolver(path)
    p1, p2 = gs.run()
    print(p1)
    print(p2)


main()
