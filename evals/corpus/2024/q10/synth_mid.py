import sys


def parse(filename):
    grid = []
    for line in open(filename):
        line = line.strip()
        if line:
            grid.append([int(c) for c in line])
    return grid


def neighbors(grid, r, c):
    result = []
    for dr, dc in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]):
            if grid[nr][nc] == grid[r][c] + 1:
                result.append((nr, nc))
    return result


def walk(grid, r, c):
    # returns list of all summit cells reached (with duplicates for multiple paths)
    if grid[r][c] == 9:
        return [(r, c)]
    summits = []
    for nr, nc in neighbors(grid, r, c):
        summits.extend(walk(grid, nr, nc))
    return summits


def solve(grid):
    score = 0
    rating = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            if grid[r][c] == 0:
                summits = walk(grid, r, c)
                score += len(set(summits))
                rating += len(summits)
    return score, rating


def main():
    filename = sys.argv[1] if len(sys.argv) > 1 else "q10.txt"
    grid = parse(filename)
    part1, part2 = solve(grid)
    print(part1)
    print(part2)


if __name__ == "__main__":
    main()
