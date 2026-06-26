import sys


class Warehouse:
    def __init__(self, grid_text, moves_text):
        self.g = [list(r) for r in grid_text.split("\n")]
        self.m = moves_text.replace("\n", "")
        self.r = 0
        self.c = 0
        for i in range(len(self.g)):
            for j in range(len(self.g[i])):
                if self.g[i][j] == "@":
                    self.r, self.c = i, j
                    self.g[i][j] = "."

    def move(self, ch):
        # handle one move command for the narrow (part 1) warehouse
        if ch == "^":
            dr, dc = -1, 0
        elif ch == "v":
            dr, dc = 1, 0
        elif ch == "<":
            dr, dc = 0, -1
        else:
            dr, dc = 0, 1
        nr, nc = self.r + dr, self.c + dc
        k = 1
        while self.g[self.r + dr * k][self.c + dc * k] == "O":
            k += 1
        e = self.g[self.r + dr * k][self.c + dc * k]
        if e == "#":
            return
        if k == 1:
            self.r, self.c = nr, nc
        else:
            self.g[self.r + dr * k][self.c + dc * k] = "O"
            self.g[nr][nc] = "."
            self.r, self.c = nr, nc

    def run(self):
        for x in self.m:
            self.move(x)
        s = 0
        for i in range(len(self.g)):
            for j in range(len(self.g[i])):
                if self.g[i][j] == "O":
                    s += 100 * i + j
        return s


class WideWarehouse:
    def __init__(self, grid_text, moves_text):
        self.g = []
        for row in grid_text.split("\n"):
            nr = []
            for ch in row:
                if ch == "#":
                    nr += ["#", "#"]
                elif ch == "O":
                    nr += ["[", "]"]
                elif ch == ".":
                    nr += [".", "."]
                else:
                    nr += ["@", "."]
            self.g.append(nr)
        self.m = moves_text.replace("\n", "")
        self.r = 0
        self.c = 0
        for i in range(len(self.g)):
            for j in range(len(self.g[i])):
                if self.g[i][j] == "@":
                    self.r, self.c = i, j
                    self.g[i][j] = "."

    def move(self, ch):
        # one move command for the doubled (part 2) warehouse
        if ch == "^":
            dr, dc = -1, 0
        elif ch == "v":
            dr, dc = 1, 0
        elif ch == "<":
            dr, dc = 0, -1
        else:
            dr, dc = 0, 1
        if dc != 0:
            k = 1
            while self.g[self.r][self.c + dc * k] in "[]":
                k += 1
            if self.g[self.r][self.c + dc * k] == "#":
                return
            for t in range(self.c + dc * k, self.c, -dc):
                self.g[self.r][t] = self.g[self.r][t - dc]
            self.g[self.r][self.c] = "."
            self.c = self.c + dc
        else:
            seen = set()
            ok = True
            q = [(self.r + dr, self.c)]
            cells = set()
            while q:
                cr, cc = q.pop()
                if (cr, cc) in seen:
                    continue
                seen.add((cr, cc))
                v = self.g[cr][cc]
                if v == "#":
                    ok = False
                    break
                if v == "[":
                    cells.add((cr, cc))
                    cells.add((cr, cc + 1))
                    q.append((cr + dr, cc))
                    q.append((cr + dr, cc + 1))
                elif v == "]":
                    cells.add((cr, cc))
                    cells.add((cr, cc - 1))
                    q.append((cr + dr, cc))
                    q.append((cr + dr, cc - 1))
            if not ok:
                return
            ordered = sorted(cells, key=lambda p: p[0], reverse=(dr > 0))
            vals = {}
            for p in cells:
                vals[p] = self.g[p[0]][p[1]]
            for p in cells:
                self.g[p[0]][p[1]] = "."
            for p in ordered:
                self.g[p[0] + dr][p[1]] = vals[p]
            self.r = self.r + dr

    def run(self):
        for x in self.m:
            self.move(x)
        s = 0
        for i in range(len(self.g)):
            for j in range(len(self.g[i])):
                if self.g[i][j] == "[":
                    s += 100 * i + j
        return s


def main():
    d = open(sys.argv[1] if len(sys.argv) > 1 else "input.txt").read()
    a, b = d.split("\n\n")
    print(Warehouse(a, b).run())
    print(WideWarehouse(a, b).run())


if __name__ == "__main__":
    main()
