# AoC 2024 Day 14 — Restroom Redoubt

Robots on a grid (width 101 × height 103) each have a position and velocity.
Each robot moves once per second and wraps around the edges (teleporting to the
opposite side when it would leave the grid).

Input format, one robot per line:

```
p=0,4 v=3,-3
```

where `p=x,y` is the starting position and `v=dx,dy` is the velocity per second.

## Part 1
Simulate 100 seconds, then compute the **safety factor** = the product of the
robot counts in the four quadrants. Robots lying exactly on the middle row or
middle column are ignored (they do not count toward any quadrant).

## Part 2
Find the fewest number of seconds that must elapse for the robots to arrange
themselves into a picture of a Christmas tree.

## Notes for graders
- The real puzzle grid is 101 × 103. The provided example
  (`q14_example.txt`) uses an 11 × 7 grid and only Part 1 is meaningful there.
- Part 2 has no closed-form answer; solutions typically detect the tree via a
  heuristic (e.g. minimum safety factor, lowest positional variance, or the
  first second at which all robots occupy distinct cells).
