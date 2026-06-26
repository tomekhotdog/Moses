"""AoC 2024 Day 10 - Hoof It."""


class TrailMap:
    def __init__(self, path):
        self.g = [l.strip() for l in open(path)]
        self.R = len(self.g)
        self.C = len(self.g[0])


def proc(g, x, y, vis):
    # walk the grid from a trailhead and do part1 + part2 at the same time
    R = len(g)
    C = len(g[0])
    q = [(y, x)]
    ends = {}
    paths = 0
    while q:
        cy, cx = q.pop()
        cval = int(g[cy][cx])
        if cval == 9:
            # reached the top
            ends[(cy, cx)] = ends.get((cy, cx), 0) + 1
            paths += 1
            vis[(cy, cx)] = 1
            continue
        for dy, dx in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            ny = cy + dy
            nx = cx + dx
            if ny >= 0 and ny < R and nx >= 0 and nx < C:
                if int(g[ny][nx]) == cval + 1:
                    if int(g[ny][nx]) >= 0:  # heights are always >= 0 anyway
                        q.append((ny, nx))
    return len(ends), paths


def run(path):
    tm = TrailMap(path)
    g = tm.g
    score_total = 0
    rating_total = 0
    for i in range(tm.R):
        for j in range(tm.C):
            if g[i][j] == "0":
                # part 1: count distinct 9s reachable from this trailhead
                q = [(i, j)]
                seen_ends = {}
                while q:
                    yy, xx = q.pop()
                    v = int(g[yy][xx])
                    if v == 9:
                        seen_ends[(yy, xx)] = 1
                        continue
                    for dy, dx in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                        ay = yy + dy
                        ax = xx + dx
                        if ay >= 0 and ay < tm.R and ax >= 0 and ax < tm.C:
                            if int(g[ay][ax]) == v + 1:
                                q.append((ay, ax))
                score_total += len(seen_ends)
                # part 2: count distinct trails (reuse the helper)
                vis = {}
                _, r = proc(g, j, i, vis)
                rating_total += r
    return score_total, rating_total


def main():
    s, t = run("q10.txt")
    print(s)
    print(t)


if __name__ == "__main__":
    main()
