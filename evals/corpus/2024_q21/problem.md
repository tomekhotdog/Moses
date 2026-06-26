# AoC 2024 Day 21 — "Keypad Conundrum"

To type a code on a numeric keypad, a robot's arm is controlled from a
directional keypad, which is itself controlled from another directional keypad,
in a chain. You press buttons on the outermost directional keypad. Each keypad
arm must avoid a gap cell.

## Keypads

Numeric keypad (the door):

```
+---+---+---+
| 7 | 8 | 9 |
+---+---+---+
| 4 | 5 | 6 |
+---+---+---+
| 1 | 2 | 3 |
+---+---+---+
    | 0 | A |
+---+---+---+
```

The gap is the bottom-left cell (where `7` column meets the `0`/`A` row).

Directional keypad (controls a robot arm):

```
    +---+---+
    | ^ | A |
+---+---+---+
| < | v | > |
+---+---+---+
```

The gap is the top-left cell.

An arm starts aimed at `A`. To press a button, you move the arm over it (using
`<`, `>`, `^`, `v` on the controlling pad) and then press `A`. The arm must
never pass over the gap cell.

## Task

Find the shortest button sequence (on the outermost directional keypad you
operate) to enter each code. A code's complexity = (shortest sequence length) ×
(numeric part of the code, e.g. `029A` → 29). Sum the complexities of all codes.

- **Part 1:** 2 intermediate directional keypads between you and the door.
- **Part 2:** 25 intermediate directional keypads. This requires memoized
  recursion over `(button-pair, depth)` computing lengths only — the literal
  sequences become astronomically long, so only the costs are tracked.

## Example input

```
029A
980A
179A
456A
379A
```

Part 1 answer for this example: `126384`.
