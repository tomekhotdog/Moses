import sys


def parse(path):
    grid_text, move_text = open(path).read().split("\n\n")
    grid = [list(row) for row in grid_text.splitlines()]
    moves = move_text.replace("\n", "")
    return grid, moves


def find_robot(grid):
    for r in range(len(grid)):
        for c in range(len(grid[r])):
            if grid[r][c] == "@":
                return r, c
    return None


deltas = {"^": (-1, 0), "v": (1, 0), "<": (0, -1), ">": (0, 1)}


def part1(grid, moves):
    grid = [row[:] for row in grid]
    r, c = find_robot(grid)
    grid[r][c] = "."
    for move in moves:
        dr, dc = deltas[move]
        # walk forward over any boxes
        steps = 1
        while grid[r + dr * steps][c + dc * steps] == "O":
            steps += 1
        if grid[r + dr * steps][c + dc * steps] == "#":
            continue
        # shift the box chain by writing into the far end
        if steps > 1:
            grid[r + dr * steps][c + dc * steps] = "O"
        grid[r + dr][c + dc] = "."
        r, c = r + dr, c + dc
    return sum(
        100 * r + c
        for r in range(len(grid))
        for c in range(len(grid[r]))
        if grid[r][c] == "O"
    )


def widen(grid):
    mapping = {"#": "##", "O": "[]", ".": "..", "@": "@."}
    return [list("".join(mapping["".join(ch)] for ch in row)) for row in grid]


def part2(grid, moves):
    grid = widen(grid)
    r, c = find_robot(grid)
    grid[r][c] = "."
    for move in moves:
        dr, dc = deltas[move]
        if dc != 0:
            steps = 1
            while grid[r][c + dc * steps] in "[]":
                steps += 1
            if grid[r][c + dc * steps] == "#":
                continue
            for col in range(c + dc * steps, c, -dc):
                grid[r][col] = grid[r][col - dc]
            grid[r][c] = "."
            c = c + dc
            continue

        # vertical: gather the connected group of box cells
        to_check = [(r + dr, c)]
        moving = set()
        blocked = False
        while to_check:
            cr, cc = to_check.pop()
            if (cr, cc) in moving:
                continue
            tile = grid[cr][cc]
            if tile == "#":
                blocked = True
                break
            if tile == ".":
                continue
            if tile == "[":
                pair = (cr, cc + 1)
            else:
                pair = (cr, cc - 1)
            moving.add((cr, cc))
            moving.add(pair)
            to_check.append((cr + dr, cc))
            to_check.append((cr + dr, pair[1]))
        if blocked:
            continue
        saved = {cell: grid[cell[0]][cell[1]] for cell in moving}
        for cell in moving:
            grid[cell[0]][cell[1]] = "."
        for (cr, cc), tile in saved.items():
            grid[cr + dr][cc] = tile
        r, c = r + dr, c

    return sum(
        100 * r + c
        for r in range(len(grid))
        for c in range(len(grid[r]))
        if grid[r][c] == "["
    )


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"
    grid, moves = parse(path)
    print(part1(grid, moves))
    print(part2(grid, moves))
