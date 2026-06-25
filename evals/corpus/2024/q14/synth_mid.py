"""AoC 2024 Day 14 - middling quality solution.

Works correctly but mixes concerns: parsing, simulation, and the part 2
heuristic all live in long functions, dims are passed around loosely, and the
tree detection uses the min-safety-factor trick without much abstraction.
"""
import math
import sys

WIDTH = 101
HEIGHT = 103


def parse(path):
    robots = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        p, v = line.split(" ")
        px, py = p[2:].split(",")
        vx, vy = v[2:].split(",")
        robots.append([int(px), int(py), int(vx), int(vy)])
    return robots


def safety(robots, t):
    counts = [0, 0, 0, 0]
    for px, py, vx, vy in robots:
        x = (px + vx * t) % WIDTH
        y = (py + vy * t) % HEIGHT
        if x == WIDTH // 2 or y == HEIGHT // 2:
            continue
        idx = 0
        if x > WIDTH // 2:
            idx += 1
        if y > HEIGHT // 2:
            idx += 2
        counts[idx] += 1
    return math.prod(counts)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "q14.txt"
    robots = parse(path)

    print("Part 1:", safety(robots, 100))

    # The tree frame has robots bunched into one region, so the safety factor
    # (product across quadrants) is minimised. Search one full period.
    best_t = 0
    best_score = None
    for t in range(WIDTH * HEIGHT):
        score = safety(robots, t)
        if best_score is None or score < best_score:
            best_score = score
            best_t = t
    print("Part 2:", best_t)


if __name__ == "__main__":
    main()
