# AoC 2023 Day 2 — Cube Conundrum

Each game shows several reveals of red, green, and blue cubes drawn from a bag.
Input lines look like:

```
Game 1: 3 blue, 4 red; 1 red, 2 green, 6 blue; 2 green
```

## Part 1
Sum the IDs of the games that would be possible if the bag contained only
**12 red, 13 green, 14 blue** cubes — i.e. every reveal in the game is within
those limits.

## Part 2
For each game compute its *power* = the product of the minimum number of red,
green, and blue cubes needed to make the game possible (the maximum count seen
of each colour across all reveals). Sum the powers of all games.
