import time

from concurrent.futures import ThreadPoolExecutor

from multiprocessing import cpu_count

tp = ThreadPoolExecutor(cpu_count())

def threaded(fn):

    def wrapper(*args, **kwargs):

        return tp.submit(fn, *args, **kwargs)

    return wrapper

def get_lines(test=False):

    with open(("test" if test else "input") + ".txt") as file:

        for ln in file:

            yield ln.strip()

class Point:

    def __init__(self, x, y):

        self.x = x

        self.y = y

    def __str__(self):

        return f"({self.x},{self.y})"

    def __eq__(self, other):

        return self.x == other.x and self.y == other.y

    def __hash__(self):

        return hash((self.x, self.y))

    def __add__(self, other):

        if isinstance(other, Point):

            return Point(self.x + other.x, self.y + other.y)

        return NotImplemented

    def opposite(self):

        return Point(-self.x, -self.y)

class TrailFinder:

    _map = []

    _directions = []

    _paths_from_trail_heads = []

    _use_recursion = False

    def __init__(self, lines, recursive=False, multithreaded=False):

        self._parse_input(lines)

        self._directions = [Point(x, y) for x, y in [(0, 1), (1, 0), (0, -1), (-1, 0)]]

        self._use_recursion = recursive

        start = time.time()

        self._paths_from_trail_heads = (

            self._find_paths_from_trail_heads_multithreaded()

            if multithreaded

            else self._find_paths_from_trail_heads()

        )

        print(

            f"Running with recursion {recursive} and multithreading {multithreaded} took {time.time() - start} seconds"

        )

    def scores(self):

        return sum([len(set(paths)) for paths in self._paths_from_trail_heads])

    def ratings(self):

        return sum([len(paths) for paths in self._paths_from_trail_heads])

    def _find_paths_from_trail_heads(self):

        return [

            (

                self._trail_score_recursive(trail_head, 0, self._directions)

                if self._use_recursion

                else self._trail_score_loop(trail_head, 0)

            )

            for trail_head in self._trail_heads()

        ]

    def _find_paths_from_trail_heads_multithreaded(self):

        futures = [self._trail_score(trail_head) for trail_head in self._trail_heads()]

        return [future.result() for future in futures]

    @threaded

    def _trail_score(self, point):

        result = (

            self._trail_score_recursive(point, 0, self._directions)

            if self._use_recursion

            else self._trail_score_loop(point, 0)

        )

        return result

    def _trail_score_recursive(self, point, height, directions):

        return (

            [point]

            if height == 9

            else [

                high_point

                for direction in directions

                for high_point in self._trail_score_recursive(

                    point + direction,

                    height + 1,

                    self._directions_without_opposite(direction),

                )

                if self._map_height(point + direction) == height + 1

            ]

        )

    def _trail_score_loop(self, start_point, start_height):

        stack = [(start_point, start_height, self._directions)]

        result = []

        while stack:

            point, height, directions = stack.pop()

            if height == 9:

                result.append(point)

            else:

                for direction in directions:

                    next_point = point + direction

                    if self._map_height(next_point) == height + 1:

                        stack.append(

                            (

                                next_point,

                                height + 1,

                                self._directions_without_opposite(direction),

                            )

                        )

        return result

    def _directions_without_opposite(self, direction):

        return [d for d in self._directions if d != direction.opposite()]

    def _map_height(self, point):

        return (

            self._map[point.x][point.y]

            if 0 <= point.x < len(self._map) and 0 <= point.y < len(self._map[0])

            else -1

        )

    def _trail_heads(self):

        return [

            Point(xx, yy)

            for xx, row in enumerate(self._map)

            for yy, col in enumerate(row)

            if col == 0

        ]

    def _parse_input(self, lines):

        self._map = [list(map(int, line)) for line in lines]

if __name__ == "__main__":

    finder = TrailFinder(get_lines(), recursive=True, multithreaded=False)

    print("1:", finder.scores())

    print("2:", finder.ratings())
