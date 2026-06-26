# AoC 2023 Day 5: If You Give A Seed A Fertilizer

An almanac lists a set of **seeds** and a chain of maps (seed → soil → fertilizer → water → light → temperature → humidity → location). Each map is made of lines `dest_start src_start length` that define range remappings: a source value `v` in `[src_start, src_start + length)` maps to `dest_start + (v - src_start)`. Any value not covered by a map's ranges passes through unchanged.

**Part 1** asks for the lowest **location** number that corresponds to any of the listed seed numbers, after running each seed through the full chain of maps.

**Part 2** reinterprets the seeds line as a list of (start, length) pairs describing **ranges** of seeds. Find the lowest location number over all seeds in all those (very large) ranges. Brute force is infeasible; this requires mapping intervals through each map, splitting ranges at boundaries rather than iterating individual values.
