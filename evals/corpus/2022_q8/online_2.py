from typing import Tuple


class Solution(StrSplitSolution):
    def parse_grid(self) -> int:
        self.grid = [[int(i) for i in row] for row in self.input]
        assert len(self.grid) == len(self.grid[0]), "not a square grid"
        return len(self.grid)

    def is_visible_from_above(self, row: int, col: int) -> Tuple[bool, int]:
        i = -100
        for i, _ in enumerate(range(row - 1, -1, -1)):
            if self.grid[row - 1 - i][col] >= self.grid[row][col]:
                return False, i
        return True, i

    def is_visible_from_below(self, row: int, col: int) -> Tuple[bool, int]:
        i = -100
        for i, _ in enumerate(range(row + 1, len(self.grid))):
            if self.grid[row + 1 + i][col] >= self.grid[row][col]:
                return False, i
        return True, i

    def is_visible_from_left(self, row: int, col: int) -> Tuple[bool, int]:
        i = -100
        for i, other_tree in enumerate(reversed(self.grid[row][:col])):
            if other_tree >= self.grid[row][col]:
                return False, i
        return True, i

    def is_visible_from_right(self, row: int, col: int) -> Tuple[bool, int]:
        i = -100
        for i, other_tree in enumerate(self.grid[row][col + 1:]):
            if other_tree >= self.grid[row][col]:
                return False, i
        return True, i

    def is_visible(self, row: int, col: int) -> Tuple[bool, int]:
        is_visible = False
        result = 1
        for func in (
            self.is_visible_from_above,
            self.is_visible_from_right,
            self.is_visible_from_below,
            self.is_visible_from_left,
        ):
            visible, dist = func(row, col)
            is_visible = is_visible or visible
            result *= dist + 1
        return is_visible, result

    def solve(self) -> Tuple[int, int]:
        grid_size = self.parse_grid()
        num_visible_trees = grid_size * 2 + (grid_size - 2) * 2
        best_view = 0

        for row in range(1, grid_size - 1):
            for col in range(1, grid_size - 1):
                if self.grid[row][col] == 0:
                    continue
                visible, view_score = self.is_visible(row, col)
                num_visible_trees += visible
                best_view = max(best_view, view_score)

        return num_visible_trees, best_view
