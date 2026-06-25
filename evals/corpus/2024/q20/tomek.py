from main import read_input

class RaceTrack:
    def __init__(self, track_width, track_height, start, end, track, walls):
        self.track_width = track_width
        self.track_height = track_height
        self.start = start
        self.end = end
        self.track = track
        self.walls = walls

    def neighbouring_track(self, location):
        x, y = location
        neighbouring = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
        return [x for x in neighbouring if x in self.track]

    def explore_track(self):
        distances_memo = { self.end: 0 }
        to_explore = self.neighbouring_track(self.end)
        while len(to_explore) > 0:
            location = to_explore.pop(0)
            neighbours = self.neighbouring_track(location)
            distance = min([distances_memo[x] + 1 for x in neighbours if x in distances_memo])
            distances_memo[location] = distance
            to_visit = [x for x in neighbours if x not in distances_memo or distances_memo[x] > (distance + 1)]
            to_explore += to_visit

        return distances_memo

    def minimum_time(self):
        return self.explore_track()[self.start]

def parse_racetrack(filename):
    lines = read_input(filename)
    start, end, track, walls = None, None, set(), set()
    width, height = len(lines[0]), len(lines)
    for y in range(height):
        for x in range(width):
            elem = lines[y][x]
            if elem == 'S':
                start = (x, y)
            elif elem == 'E':
                end = (x, y)
            elif elem == '.':
                track.add((x, y))
            elif elem == '#':
                walls.add((x, y))
            else:
                raise Exception(f"Unexpected element! {elem}")
    if start is None:
        raise Exception("Failed to find start element!")
    if end is None:
        raise Exception("Failed to find end element!")
    track.add(start)
    track.add(end)
    return RaceTrack(width, height, start, end, track, walls)

def manhattan_distance(location1, location2):
    x1, y1 = location1
    x2, y2 = location2
    return abs(x1 - x2) + abs(y1 - y2)

"""
Idea is to take every pair of locations along the racetrack. A cheat is possible if the manhattan distance is less 
than the maximum cheat length and the saving is equal to the distance saved minus the cost of the cheat.
<remarks>
The length of our input racetrack is ~10k, resulting in ~(10_000^2)/2 cheats to inspect. Execution time is ~15s
</remarks
"""
def explore_cheats(racetrack, maximum_distance):
    explored = racetrack.explore_track()
    route = list(reversed(explored.keys()))
    cheat_savings = {}
    for cheat_start_index in range(len(route)):
        for cheat_end_index in range(cheat_start_index, len(route)):
            cheat_start = route[cheat_start_index]
            cheat_end = route[cheat_end_index]
            cheat_length = manhattan_distance(cheat_start, cheat_end)
            if cheat_length > maximum_distance:
                continue
            cheat_saving = explored[cheat_start] - explored[cheat_end] - cheat_length
            if cheat_saving > 0:
                cheat_savings[(cheat_start, cheat_end)] = cheat_saving

    return cheat_savings

def part1() -> int:
    racetrack = parse_racetrack('q20.txt')
    return len([x for x in explore_cheats(racetrack, 2).values() if x >= 100])

def part2() -> int:
    racetrack = parse_racetrack('q20.txt')
    return len([x for x in explore_cheats(racetrack, 20).values() if x >= 100])

print(part1())
print(part2())