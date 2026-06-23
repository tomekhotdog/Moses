# Calibration corpus — Moses vs Judge (2024)

## q16

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 115 | 87.1 | A | 82 | +5.1 | #14:36, #15:50, #1:52 | Strong domain modelling (Vec/State/Maze), type hints, docstrings, and a correct predecessor-DAG backtrack, marred only by a dead/confused best_cost_to_end helper and an awkward end-state reconstruction. |
| tomek.py | 127 | 86.03 | A | 62 | +24.0 | #25:21, #1:33, #14:50 | Clear OO modelling and naming with good decomposition, but uses a FIFO list (pop(0)) rather than a priority queue and a hacky (start+end)%2 rotation-cost formula, making correctness fragile and over-modelled via the Step class. |
| online_2.py | 118 | 75.93 | B | 58 | +17.9 | #15:0, #17:0, #25:15 | Readable with named constants and a direction model, but duplicates two near-identical Dijkstras and pushes whole path-sets through the heap for Part 2, plus a hardcoded Windows input path. |
| synth_primitive.py | 73 | 67.41 | B | 48 | +19.4 | #12:0, #16:0, #25:0 | A correct, compact Dijkstra-plus-backtrack for both parts but with no structure, pervasive single-letter names, magic numbers, and redundant setdefault calls that hurt readability. |
| online_1.py | 51 | 92.75 | A | 28 | +64.8 | #25:0, #6:83, #1:85 | Wholesale copies the heapq-docs lazy-deletion PQ recipe it never needs, uses single-letter state, deeply nested inline conditionals with repeated index arithmetic and magic 1000000, and only solves Part 1. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.0** (n=5)

## q4

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 65 | 88.84 | A | 88 | +0.8 | #1:25, #21:50, #5:84 | Clean domain modelling with Point/Grid abstractions, a generic spells_word helper, type hints and tidy part decomposition; only mildly over-engineered for the problem size. |
| synth_mid.py | 40 | 84.74 | A | 82 | +2.7 | #14:35, #1:36, #24:80 | Idiomatic, simple and readable with well-named helpers (in_bounds, count_xmas/count_x_mas) and clear direction handling, hitting the sweet spot of clarity without ceremony. |
| online_2.py | 37 | 81.85 | A | 70 | +11.8 | #15:0, #21:50, #14:52 | Sound diagonal-bucketing approach with helpful comments and a fine part2, but the verbose diagonal dict-building and the opaque _set name hold it back. |
| online_1.py | 39 | 89.13 | A | 64 | +25.1 | #25:0, #1:56, #3:100 | Compact and clever numpy/regex solution with rare file-error handling, but inconsistent 1/2-space indentation, terse lambdas and isSM naming make it cryptic to read. |
| synth_primitive.py | 37 | 78.14 | B | 38 | +40.1 | #12:0, #14:0, #24:33 | Functionally correct but a single monolithic solve() with module-level I/O, single-letter names and both parts crammed into one deeply nested loop, with no decomposition. |
| tomek.py | 79 | 63.94 | C | 30 | +33.9 | #16:0, #25:0, #14:0 | Over-engineered yet incomplete: a confusing transpose/flip in read_grid inverts coordinate semantics, per-direction hardcoded offset lists duplicate heavily, it imports from a nonexistent module, and main runs only part2 leaving part1 dead. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.657** (n=6)

## q9

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 88 | 86.96 | A | 90 | -3.0 | #27:11, #15:38, #25:55 | Clean per-block model with a FREE sentinel, small single-purpose functions each documented, full type hints, and a proper main guard make this the most readable and well-decomposed solution. |
| online_2.py | 68 | 90.06 | A | 72 | +18.1 | #15:0, #25:0, #27:28 | Idiomatic and well-typed with a tidy Item dataclass and expand/parse helpers, but the two separately-redefined Solution classes, duplicated imports, and subtle list insert/mutate logic in part 2 reduce clarity. |
| online_1.py | 108 | 79.08 | B | 60 | +19.1 | #15:0, #27:0, #12:19 | A reasonable Block abstraction with decent naming, but it conflates file lists, type flags, and space lengths into one struct and relies on try/except as control flow, making the stateful compaction hard to follow. |
| tomek.py | 105 | 90.4 | A | 52 | +38.4 | #15:0, #14:59, #25:62 | Helpful worked-example comments and an explicit FileBlock type, but redundant per-block file_length storage, tangled nested loops in compact_contiguous, and leftover debug prints undercut it. |
| synth_primitive.py | 70 | 73.19 | B | 28 | +45.2 | #12:0, #15:0, #24:0 | A single monolithic function with pervasive one-letter names (d, f, l, r, m, st, ln), no types, no docstrings, and inlined part1/part2 logic makes it correct but very hard to read or maintain. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.3** (n=5)

## Summary

| Question | Spearman ρ | n |
|---|---|---|
| q16 | 0.0 | 5 |
| q4 | 0.657 | 6 |
| q9 | 0.3 | 5 |
