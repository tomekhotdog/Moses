# Advent of Code 2024, Day 20: Race Condition

A racetrack is given as a grid where `#` are walls, `S` is the start tile, and `E` is the end tile. There is exactly one path (single track, no branches) from `S` to `E`. Normally you must follow the track one tile per picosecond.

Once during the race you may "cheat": for a limited number of picoseconds your moves may pass through walls, ignoring collision. The cheat begins when you first leave the track and ends when you next return to a track tile. Each cheat is uniquely identified by its start and end position.

**Part 1:** Cheats may last at most 2 picoseconds. Count how many distinct cheats would save at least 100 picoseconds compared to the normal best time.

**Part 2:** Same, but cheats may last at most 20 picoseconds. Count how many distinct cheats save at least 100 picoseconds.

(The worked example in the puzzle uses a lower save threshold; the real answer uses a threshold of 100.)
