# AoC 2024 Day 15 — Warehouse Woes

A robot (`@`) in a warehouse grid follows a movement string made of `^v<>`,
pushing boxes (`O`) — including chains of boxes — when there is space, and is
blocked by walls (`#`).

The input has two sections separated by a blank line: the warehouse grid, then
the movement string (which may span several lines and should be concatenated).

## Part 1
Simulate every move. When the robot moves toward one or more boxes, the whole
chain shifts by one cell if the cell beyond the last box is empty; if a wall
blocks the chain, nothing moves. After all moves, sum each box's **GPS
coordinate**, defined as `100 * row + col`.

## Part 2
The warehouse is doubled in width before simulating: every `#` becomes `##`,
every `O` becomes `[]`, every `.` becomes `..`, and `@` becomes `@.`. Boxes are
now two cells wide (`[]`). Horizontal pushes behave like Part 1, but vertical
pushes can fan out: pushing one wide box may push several wide boxes above or
below it, and the whole connected group moves only if every cell it would enter
is free. Sum the GPS coordinate (`100 * row + col`) of each box's **left edge**
(`[`).
