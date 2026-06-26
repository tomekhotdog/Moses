"""Advent of Code 2024, Day 16 - Reindeer Maze.

A uniform-cost (Dijkstra) search over states of (position, facing). Moving
forward costs MOVE_COST; rotating 90 degrees costs TURN_COST.
"""

from __future__ import annotations

import heapq
import sys
from collections import defaultdict
from dataclasses import dataclass

MOVE_COST = 1
TURN_COST = 1000

WALL = "#"
START = "S"
END = "E"


@dataclass(frozen=True)
class Vec:
    """A 2D position or direction in (row, col) space."""

    row: int
    col: int

    def __add__(self, other: "Vec") -> "Vec":
        return Vec(self.row + other.row, self.col + other.col)

    def turn_left(self) -> "Vec":
        return Vec(-self.col, self.row)

    def turn_right(self) -> "Vec":
        return Vec(self.col, -self.row)


EAST = Vec(0, 1)


@dataclass(frozen=True)
class State:
    """The reindeer at a position, facing a direction."""

    pos: Vec
    facing: Vec


@dataclass
class Maze:
    walls: set[Vec]
    start: Vec
    end: Vec

    @classmethod
    def parse(cls, text: str) -> "Maze":
        walls: set[Vec] = set()
        start = end = None
        for r, line in enumerate(text.splitlines()):
            for c, char in enumerate(line):
                pos = Vec(r, c)
                if char == WALL:
                    walls.add(pos)
                elif char == START:
                    start = pos
                elif char == END:
                    end = pos
        assert start is not None and end is not None, "maze missing S or E"
        return cls(walls, start, end)

    def is_open(self, pos: Vec) -> bool:
        return pos not in self.walls


def neighbours(maze: Maze, state: State) -> list[tuple[State, int]]:
    """Return (next_state, step_cost) options from the given state."""
    options: list[tuple[State, int]] = []
    ahead = state.pos + state.facing
    if maze.is_open(ahead):
        options.append((State(ahead, state.facing), MOVE_COST))
    options.append((State(state.pos, state.facing.turn_left()), TURN_COST))
    options.append((State(state.pos, state.facing.turn_right()), TURN_COST))
    return options


def search(maze: Maze) -> tuple[int, dict[State, list[State]]]:
    """Dijkstra from the start. Returns best cost and a predecessor map
    recording every predecessor lying on a lowest-cost path."""
    start = State(maze.start, EAST)
    best_cost: dict[State, int] = {start: 0}
    predecessors: dict[State, list[State]] = defaultdict(list)
    frontier: list[tuple[int, int, State]] = [(0, 0, start)]
    tie = 1
    final_cost = None

    while frontier:
        cost, _, state = heapq.heappop(frontier)
        if cost > best_cost.get(state, float("inf")):
            continue
        if state.pos == maze.end and final_cost is None:
            final_cost = cost

        for nxt, step in neighbours(maze, state):
            new_cost = cost + step
            known = best_cost.get(nxt)
            if known is None or new_cost < known:
                best_cost[nxt] = new_cost
                predecessors[nxt] = [state]
                heapq.heappush(frontier, (new_cost, tie, nxt))
                tie += 1
            elif new_cost == known:
                predecessors[nxt].append(state)

    assert final_cost is not None, "no path to end"
    return final_cost, predecessors


def best_cost_to_end(maze: Maze, best: int, preds: dict[State, list[State]]) -> int:
    """Find every End state reached at the best cost."""
    # Recompute via best_cost would be cleaner, but we derive ends from preds.
    return best


def count_best_path_tiles(maze: Maze, best: int, preds: dict[State, list[State]]) -> int:
    end_states = [State(maze.end, d) for d in (EAST, EAST.turn_left(), EAST.turn_right(), EAST.turn_left().turn_left())]
    reachable = [s for s in end_states if s in preds or s.pos == maze.end]
    tiles: set[Vec] = set()
    stack = list(reachable)
    seen: set[State] = set()
    while stack:
        state = stack.pop()
        if state in seen:
            continue
        seen.add(state)
        tiles.add(state.pos)
        stack.extend(preds.get(state, []))
    return len(tiles)


def main() -> None:
    text = sys.stdin.read() if not sys.argv[1:] else open(sys.argv[1]).read()
    maze = Maze.parse(text)
    best, preds = search(maze)
    print(best)
    print(count_best_path_tiles(maze, best, preds))


if __name__ == "__main__":
    main()
