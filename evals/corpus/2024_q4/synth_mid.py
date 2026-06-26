def read_grid(filename):
    with open(filename) as f:
        return [line.rstrip("\n") for line in f if line.strip()]


def in_bounds(grid, r, c):
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])


def count_xmas(grid):
    directions = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    word = "XMAS"
    total = 0
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            for dr, dc in directions:
                ok = True
                for i, ch in enumerate(word):
                    nr, nc = r + dr * i, c + dc * i
                    if not in_bounds(grid, nr, nc) or grid[nr][nc] != ch:
                        ok = False
                        break
                if ok:
                    total += 1
    return total


def count_x_mas(grid):
    total = 0
    for r in range(1, len(grid) - 1):
        for c in range(1, len(grid[0]) - 1):
            if grid[r][c] != "A":
                continue
            diag1 = grid[r - 1][c - 1] + grid[r + 1][c + 1]
            diag2 = grid[r - 1][c + 1] + grid[r + 1][c - 1]
            if diag1 in ("MS", "SM") and diag2 in ("MS", "SM"):
                total += 1
    return total


def main():
    grid = read_grid("input.txt")
    print("Part 1:", count_xmas(grid))
    print("Part 2:", count_x_mas(grid))


if __name__ == "__main__":
    main()
