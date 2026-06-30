# Calibration corpus — Moses vs Judge

## 2022_q11

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 68 | 91.07 | A | 92 | -0.9 | #25:0, #27:16, #15:38 | Excellent readability with a focused Monkey dataclass, well-named constants, a single elegant simulation loop, clear docstrings, and the modulus computed unconditionally for simplicity—idiomatic and very pleasant to read. |
| online_2.py | 72 | 84.89 | A | 78 | +6.9 | #15:0, #25:0, #24:26 | Clean, well-decomposed solution with a clear namedtuple model and a unified solve function, though it depends on several heavy external libraries (aocd, funcy, parse) and uses terse names like l1/iftrue and a separate inspect helper that add slight friction. |
| tomek.py | 133 | 82.39 | A | 72 | +10.4 | #3:0, #25:0, #30:10 | Strong domain modelling with cohesive classes and validation, but it is over-engineered for the task with redundant lambda indirection (parse_operand returning closures), repetitive raise-on-substring parsing, and an external main-module dependency that add bulk without proportional clarity. |
| synth_primitive.py | 50 | 87.68 | A | 48 | +39.7 | #15:0, #25:0, #24:54 | Straightforward and readable at the statement level but models monkeys as six parallel dictionaries with single-letter names and relies on eval, scattering one entity's data across structures that must be kept in sync. |
| online_1.py | 110 | 46.4 | D | 7 | +39.4 | #16:0, #25:9, #17:100 | A single nested print statement of deeply layered lambdas, eval, and tuple-index side effects that is essentially unreadable and unmaintainable, sacrificing all clarity for obfuscated cleverness. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.7** (n=5)

## 2022_q2

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 81 | 84.93 | A | 93 | -8.1 | #16:0, #25:1, #1:43 | Exemplary: enums encode their scores as values, domain functions (outcome_against, shape_for_outcome, score_round) read as the rules themselves, parsing is robust, and parse/compute/IO are cleanly separated with full type hints. |
| online_1.py | 79 | 88.43 | A | 80 | +8.4 | #21:0, #25:0, #27:21 | Clean Move enum with well-named domain methods and clear part split; held back by duplicated file-reading, a missing type hint on opp_move, and move_score reimplementing what enum values could carry. |
| tomek.py | 98 | 76.95 | B | 72 | +5.0 | #16:0, #25:0, #30:0 | Strong domain types (Play, DecypherStrategy, Round) and good type hints, but over-engineered: parse_my_play bundles two strategies into one branchy function with an exhaustive nine-case match where a small map would do, and Round carries no behavior. |
| online_2.py | 80 | 81.13 | A | 36 | +45.1 | #16:0, #25:0, #27:0 | Hard to read and outright broken: is_lose recurses on itself infinitely, scores via arithmetic on booleans, maintains two parallel inconsistent mapping schemes, and flips tuple argument order between functions. |
| synth_primitive.py | 76 | 66.48 | B | 30 | +36.5 | #25:0, #12:12, #14:27 | Functionally correct but deliberately primitive—single-letter names throughout, nested if/elif chains, magic-string comparisons, and a self-admitted copy-paste of p1 logic into p2 with no abstraction. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.8** (n=5)

## 2022_q8

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 76 | 96.05 | A | 93 | +3.0 | #1:35, #21:50, #24:75 | Cleanly factored with a reusable `_ray` abstraction, consistent row/col naming, a module docstring, and tidy top-level functions; the most elegant and readable of the set. |
| synth_mid.py | 48 | 93.14 | A | 84 | +9.1 | #1:27, #5:72, #24:73 | Compact and very readable with a shared `line_of_sight` generator and DIRECTIONS table eliminating duplication; loses a little only for the flat function-based design without a grid abstraction. |
| tomek.py | 68 | 74.1 | B | 80 | -5.9 | #16:0, #30:0, #25:12 | Well-decomposed with an Enum-driven direction model and clear function names, but the underused Forest wrapper, threaded forest argument everywhere, and an external read_input dependency add mild ceremony. |
| online_1.py | 99 | 92.08 | A | 72 | +20.1 | #16:0, #27:74, #1:82 | Clear domain model with descriptive names and docstrings, but redundant generator wrapping, a confusing x/y vs row/col axis muddle, and a hidden-trees-then-subtract detour add unnecessary friction. |
| online_2.py | 55 | 82.33 | A | 38 | +44.3 | #16:0, #25:0, #27:0 | Four near-identical direction methods, a magic `i = -100` sentinel, a brittle `square grid` assumption, and a confusing dual-purpose return tuple make this hard to follow despite type hints. |
| synth_primitive.py | 83 | 57.98 | C | 22 | +36.0 | #16:0, #12:2, #14:52 | One giant `go` function with eight nearly-identical inlined direction loops, single-letter names throughout, and zero decomposition makes this tedious and error-prone to read. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.829** (n=6)

## 2023_q1

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 52 | 90.29 | A | 93 | -2.7 | #25:0, #27:0, #1:52 | Exemplary: precise docstrings and types, clean decomposition into small single-purpose functions, tasteful walrus use, anchored matching that expresses overlap handling clearly, and a proper ValueError on empty input. |
| online_1.py | 28 | 97.31 | A | 74 | +23.3 | #27:0, #1:40, #2:100 | Compact and readable with a well-commented replace trick that elegantly preserves overlaps, though the cleverness needs that comment and an assert is weak error handling. |
| online_2.py | 35 | 95.44 | A | 52 | +43.4 | #27:0, #25:43, #1:88 | Works but has two near-duplicate functions, shadows the builtin sum, an unexplained cryptic regex lookahead, a needless 'zero' entry, and no handling for empty lines. |
| tomek.py | 46 | 89.29 | A | 48 | +41.3 | #25:0, #27:0, #1:66 | Has types and comments but mutates a module-global list across calls, over-engineers with find-all-then-sort instead of a simple scan, raises a bare Exception, and depends on a missing main module. |
| synth_primitive.py | 49 | 84.72 | A | 24 | +60.7 | #24:9, #25:18, #14:36 | Deliberately primitive: a god function with manual index arithmetic, magic numbers, one- and two-letter names, integer flags, duplicated part1/part2, and silent zero on no digits. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.7** (n=5)

## 2023_q11

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 66 | 93.46 | A | 93 | +0.5 | #25:9, #27:52, #1:55 | Excellent domain modelling with frozen dataclasses, clear names, named constants, docstrings, and clean immutable transformations that make the solution pleasant to read. |
| online_2.py | 48 | 92.29 | A | 74 | +18.3 | #25:0, #1:37, #14:85 | Well-decomposed with good function boundaries and use of combinations, but cluttered by external decorators, hardcoded answer asserts, and slightly confusing x/y-vs-row/col naming. |
| online_1.py | 14 | 72.73 | B | 68 | +4.7 | #25:0, #16:100, #17:100 | Terse and readable for its size with clean comprehensions, but no decomposition or error handling and the inline per-step `scale` accumulation loop is less clear than a direct distance computation. |
| tomek.py | 58 | 78.74 | B | 47 | +31.7 | #16:0, #30:0, #1:23 | Typed and named reasonably but over-engineered with redundant Universe/UniversePair classes, fragile string-concatenation hashing, and a wasteful build-all-ordered-pairs-then-dedup approach duplicated across part1/part2. |
| synth_primitive.py | 84 | 53.59 | C | 31 | +22.6 | #16:0, #24:0, #12:4 | Functional but cryptic single-letter names, flag-based loops, magic numbers, and Part 2 copy-pasted wholesale from Part 1 make it hard and unpleasant to read. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.9** (n=5)

## 2023_q2

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 61 | 92.82 | A | 93 | -0.2 | #25:2, #1:30, #27:50 | Exemplary domain modelling with Reveal/Game abstractions exposing intent-revealing methods, named constants, full typing, a clear linear parse pipeline, and a docstring — easy and pleasant to read. |
| online_2.py | 66 | 89.59 | A | 80 | +9.6 | #15:0, #25:9, #27:21 | Clean typed dataclass and enum modelling with a single shared parser and well-named code, marred only by the slightly clunky manual flag-and-break loop in part_one where part_two is more elegant. |
| tomek.py | 70 | 84.26 | A | 66 | +18.3 | #25:0, #30:0, #1:32 | Genuine domain abstractions (Bag/Round/Game/Colour) but undermined by cramped single-letter attributes, verbose list(map(lambda)) idioms over comprehensions, and an assert used for input validation. |
| online_1.py | 31 | 92.01 | A | 47 | +45.0 | #25:0, #21:50, #24:60 | Functionally compact but clever to a fault — string-replace tricks, map(str.split) chains, _sum/_set naming, dead one-liner comments, and duplicated parsing make it taxing to follow. |
| synth_primitive.py | 60 | 64.3 | C | 35 | +29.3 | #14:0, #25:0, #12:10 | Crude procedural code with single-character names, inline magic limits, and parsing logic fully duplicated across p1/p2 with no abstraction, making it the least readable of the set. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.7** (n=5)

## 2023_q3

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 94 | 96.37 | A | 90 | +6.4 | #15:50, #21:67, #1:72 | Well-chosen domain abstractions (Position, Number, Schematic), full typing, docstrings and cached queries make it the most readable and elegant of the set, only slightly heavy with per-cell frozensets. |
| online_1.py | 81 | 67.08 | B | 74 | -6.9 | #15:0, #25:0, #14:2 | Clear single-pass parser with helpful comments and clean decomposition, weakened by an opaque positional tuple-of-three return and extraneous aocd/print decorators. |
| tomek.py | 69 | 84.65 | A | 55 | +29.7 | #30:0, #27:19, #1:29 | Decent naming and explanatory comments but two inconsistent adjacency implementations, dense nested map/lambda expressions, and an attribute mismatch (x.raw_value vs value) make it confusing and brittle. |
| online_2.py | 88 | 60.52 | C | 48 | +12.5 | #16:0, #25:77, #17:100 | Functional flat script marred by wholesale duplication of the parsing loop across parts, mid-file import, and an over-engineered random-UUID scheme to identify numbers where an index would suffice. |
| synth_primitive.py | 69 | 58.22 | C | 38 | +20.2 | #14:0, #16:0, #25:0 | Correct but deliberately bare-bones: opaque positional tuple indexing (n[0], n[1]...), single-letter names throughout, and self-admitted duplicated neighbour math make it unpleasant to read. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.9** (n=5)

## 2023_q5

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 102 | 94.91 | A | 95 | -0.1 | #1:41, #21:50, #24:62 | Exemplary domain model with frozen dataclasses, consistent half-open intervals, full type hints, precise docstrings, and a clean interval-splitting algorithm that reads almost as prose. |
| online_2.py | 79 | 85.03 | A | 82 | +3.0 | #30:0, #25:24, #1:36 | Elegant reuse of Python's built-in range as the interval type with tidy recursive splitting and good typing, slightly marred by two single-field Solution wrapper classes, mid-file imports, and a dense four-case overlap block. |
| tomek.py | 119 | 88.79 | A | 68 | +20.8 | #25:16, #1:28, #24:36 | Solid OO domain model with descriptive names, but the map_range method is a tangle of overlapping conditionals and early returns, it carries an unused mappings_reversed field, and parsing is duplicated across the two parts. |
| synth_primitive.py | 74 | 68.47 | B | 38 | +30.5 | #25:0, #14:4, #12:12 | Correct and compact but hard to read: one god function, cryptic abbreviations (prs, sd, mps, o1/o2), raw lists indexed by position, magic slices and flags, and no types or abstractions. |
| online_1.py | 98 | 76.67 | B | 22 | +54.7 | #14:0, #16:0, #27:0 | Core logic is buried under pervasive debug prints, misleading names (do_overlap compares start to length, iter_map shadows a builtin), a function that silently returns None, dead branches, and a hardcoded asserted answer. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.8** (n=5)

## 2023_q7

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 81 | 93.26 | A | 94 | -0.7 | #25:0, #27:36, #1:58 | Exemplary: IntEnum types, an elegant shape-to-type lookup that replaces branching, a frozen dataclass, clear docstrings and type hints, and a clean classify/parse/sort/solve decomposition with linear flow. |
| synth_mid.py | 52 | 91.18 | A | 81 | +10.2 | #25:0, #15:17, #1:37 | Clean, well-named functional solution with a clear comparator and tidy parse/winnings split; only minor friction from the repetitive size-tuple if-chain and bare integer hand-type magic numbers. |
| online_2.py | 85 | 92.62 | A | 58 | +34.6 | #25:0, #14:38, #21:50 | Reasonable class structure and a test, but the full-house classification is a hard-to-parse tangle of unparenthesised and/or conditions and the winnings ranking uses convoluted index arithmetic with a misleading comment. |
| online_1.py | 45 | 79.54 | B | 45 | +34.5 | #15:0, #16:0, #24:0 | Compact but over-clever: an opaque numeric scoring trick (10*max+2nd then max-le lookup), single-letter loop vars, O(n^2) counting, and duplicated comprehension pipelines across the two parts make it hard to follow. |
| synth_primitive.py | 71 | 76.74 | B | 40 | +36.7 | #15:0, #16:0, #25:0 | Logic is sound and direct but readability is poor: cryptic single-letter names (t, h, c, v, o, s) throughout and wholesale duplication of the comparator and part1/part2 functions. |
| tomek.py | 161 | 75.64 | B | 38 | +37.6 | #16:0, #25:0, #30:0 | Heavily over-engineered for the task: a 30-line if-chain card-type mapper, a CamelCard class with hashing ceremony and a stray copy-pasted comment, a verbose joker-upgrade table, and duplicated part1/part2 all inflate complexity needlessly. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.943** (n=6)

## 2024_q10

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 76 | 96.23 | A | 93 | +3.2 | #1:35, #21:50, #25:74 | Exemplary: docstrings, type aliases, named constants, a deep TopographicMap domain class, and clean DFS/recursion that read as a direct statement of the problem. |
| synth_mid.py | 42 | 94.59 | A | 80 | +14.6 | #1:32, #25:52, #14:75 | Clear, well-decomposed functions (parse/neighbors/walk/solve) with sensible names and a single recursion computing both parts; only lacks type hints, docstrings, and named height constants. |
| online_2.py | 60 | 81.86 | A | 70 | +11.9 | #16:0, #15:17, #25:33 | Readable with full type hints and descriptive names, but the deque-as-stack with O(n) 'neighbor not in queue' membership conflates BFS/DFS concepts and the grid is parsed twice across the two parts. |
| tomek.py | 90 | 84.83 | A | 52 | +32.8 | #30:0, #25:33, #1:33 | An unused TrailMap class, duplicated traversal logic (an inline part-1 walk plus a near-identical proc helper), a dead 'height >= 0' check, dict-as-set, and terse names make it cluttered and hard to follow. |
| synth_primitive.py | 65 | 64.36 | C | 48 | +16.4 | #14:0, #15:0, #16:0 | Over-engineered around a Coordinates class with an external read_input dependency, a 999 sentinel for a '.' case the problem never has, per-iteration lambda reassignment, a magic len==10 check, and a convoluted breadth-by-trail-list traversal that materializes every full path. |
| online_1.py | 125 | 90.58 | A | 42 | +48.6 | #30:25, #1:54, #25:68 | Buried under accidental complexity: a threading decorator, dual recursion/loop implementations, mutable class-level defaults, an unnecessary opposite-direction filter, timing prints in the constructor, and noisy double-spaced formatting. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.6** (n=6)

## 2024_q12

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 111 | 97.5 | A | 92 | +5.5 | #1:56, #21:67, #14:75 | Exemplary domain modelling with cohesive Point/Grid/Region abstractions, clean flood-fill decomposition, precise naming, type hints throughout, and corner-counting factored into a readable helper. |
| online_2.py | 135 | 83.5 | A | 70 | +13.5 | #16:0, #15:17, #1:38 | Clear functional decomposition with a tidy Coordinate namedtuple and small helpers, but the Part 2 side-count rebuilds a sub-grid and re-runs flood fill, leaning on coupled corner predicates like is_not_double_corner that are hard to follow. |
| online_1.py | 95 | 81.32 | A | 62 | +19.3 | #15:0, #16:0, #25:16 | Readable class-based helpers with reasonable names, but Part 2's side-counting via grid rotation and string join/split tricks is obscure and over-clever, and parse/region-finding logic is duplicated across part1 and part2. |
| tomek.py | 125 | 91.78 | A | 55 | +36.8 | #27:0, #15:23, #25:36 | Has a genuine Region abstraction and clear comments, but region discovery is convoluted and quadratic—joining plots by scanning all existing regions while also doing DFS—mixing two redundant traversals with leftover debug cruft. |
| synth_primitive.py | 69 | 80.96 | A | 48 | +33.0 | #15:0, #14:8, #12:24 | Correct and compact with a flood-fill class, but cryptic one/two-letter names (g, fld, st, per, co, ch, hh) and perimeter plus corner logic crammed into one monolithic run() method severely hurt readability. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.7** (n=5)

## 2024_q13

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 75 | 96.4 | A | 93 | +3.4 | #25:47, #1:58, #27:67 | Exemplary: module docstring, a frozen Machine dataclass for clean domain modelling, named constants, integer-only Cramer's rule with divisibility checks avoiding float pitfalls, Optional return signalling unwinnable, and tidy decomposition into parse/solve/total/main. |
| online_2.py | 54 | 89.06 | A | 74 | +15.1 | #25:0, #1:45, #5:60 | Clear functional decomposition with a single regex parser and an adjustment-parameterized solver plus self-tests, but uses float division with int-equality checks instead of exact integer math and hardcodes a brittle Windows-style input path. |
| tomek.py | 56 | 86.26 | A | 66 | +20.3 | #16:0, #25:0, #27:0 | Genuine domain modelling via a documented Machine class with well-named methods, but relies on float arithmetic with round-then-verify (fragile at part-2 magnitudes), opaque p1..p4 field names, and an awkward int(len/4)+1 loop bound. |
| online_1.py | 45 | 81.88 | A | 48 | +33.9 | #16:0, #25:0, #24:14 | Functions correctly within its framework but suffers cryptic naming, float division with is_integer checks, large blocks of dead commented-out z3 code, magic literals, and parse logic duplicated verbatim across part1 and part2. |
| synth_primitive.py | 67 | 84.45 | A | 42 | +42.5 | #16:0, #25:0, #14:36 | Correct integer Cramer's rule, but a hollow class wrapping an untyped flat-dict model (per its own comments), with one monolithic run() method that duplicates the entire part1/part2 logic and deeply nested if i>=0: if j>=0: branching. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.9** (n=5)

## 2024_q14

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 62 | 90.38 | A | 92 | -1.6 | #25:0, #15:17, #27:26 | Clean module-level docstrings, a frozen Robot dataclass with a focused position_after method, well-decomposed pure functions with type hints, and the part-2 heuristic abstracted into named helpers make this the most readable and well-structured solution. |
| online_2.py | 67 | 89.71 | A | 78 | +11.7 | #25:0, #14:33, #27:74 | Strong domain modelling via NamedTuples (Robot/Velocity/Coordinate) and clean type-hinted parsing/printing, but it loses points for a hardcoded magic part-2 answer (seconds == 7568 / printing '7569') and an assert pinning a specific puzzle input. |
| synth_mid.py | 50 | 90.09 | A | 68 | +22.1 | #15:0, #25:0, #24:76 | Correct and reasonably readable with a clear safety helper and honest comments, but uses bare lists for robots, global WIDTH/HEIGHT, and inlines the part-2 search in main without abstraction. |
| synth_primitive.py | 55 | 79.24 | B | 64 | +15.2 | #25:0, #30:0, #24:57 | Coherent RobotSim class with readable parsing and honest comments, but tuple-index access (r[0]..r[3]), hardcoded grid/centre constants (101/103/50/51), verbose nested-if quadrant branching, and a monolithic run() that bundles both parts with no error handling keep it middling. |
| online_1.py | 61 | 75.95 | B | 60 | +16.0 | #15:0, #16:0, #25:0 | Tuple-of-tuples modelling is workable and the quadrant indexing is neat, but parsing logic is duplicated verbatim across part1/part2, the test-input detection by len==12 is hacky, and the +width/+height velocity-offset trick is opaque. |
| tomek.py | 83 | 81.95 | A | 52 | +30.0 | #25:0, #30:0, #1:28 | Has a real Robot class and named helpers, but the over-engineered generalized quadrant_counts (fractional borderline arithmetic, max(0,x-1) fudging) is hard to follow and brittle, parsing is verbose with repeated splits, and dimensions are sprinkled as loose args. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.771** (n=6)

## 2024_q15

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 130 | 95.01 | A | 92 | +3.0 | #21:50, #27:56, #15:62 | Exemplary domain modelling with a deep Warehouse dataclass, named constants, type aliases, and a single unified push-cluster BFS that elegantly handles horizontal and vertical wide-box fan-out without branch duplication. |
| tomek.py | 167 | 66.61 | B | 78 | -11.4 | #14:0, #16:0, #30:0 | Clear naming and a clean recursive can_move/move separation with explanatory comments, but parallel box sets and symmetric left/right branches add incidental state, plus top-level execution and an external import reduce self-containment. |
| online_2.py | 149 | 58.93 | C | 71 | -12.1 | #15:0, #16:0, #27:0 | Readable procedural solution with a MOVES dict and recursive pushing, but it shadows the map builtin, near-duplicates parse/move for each part, and the per-move deepcopy rollback is a clumsy way to handle blocked moves. |
| synth_mid.py | 97 | 81.33 | A | 70 | +11.3 | #15:0, #24:52, #12:56 | Tidy procedural solution with clean parsing and a clear vertical-push BFS, but it duplicates push logic across parts and leans on raw grid mutation with no domain modelling. |
| online_1.py | 142 | 52.8 | C | 57 | -4.2 | #12:0, #14:0, #15:0 | Functional and broadly readable, but heavy pt1/pt2 duplication, a tangled part2 loop that conflates partner discovery with move-checking, a brittle multi-key sort hack, and a hardcoded input path drag it down. |
| synth_primitive.py | 138 | 78.6 | B | 52 | +26.6 | #16:0, #14:33, #12:41 | Two near-duplicate Warehouse/WideWarehouse classes give some structure, but pervasive single-letter names (g, m, k, e, q, v), copy-pasted parsing and direction branches, and dead nr/nc variables keep it terse and hard to read. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.371** (n=6)

## 2024_q16

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 115 | 93.59 | A | 82 | +11.6 | #14:36, #15:50, #1:52 | Strong domain modelling (Vec/State/Maze), type hints, docstrings, and a correct predecessor-DAG backtrack, marred only by a dead/confused best_cost_to_end helper and an awkward end-state reconstruction. |
| tomek.py | 127 | 84.3 | A | 62 | +22.3 | #30:0, #25:21, #1:33 | Clear OO modelling and naming with good decomposition, but uses a FIFO list (pop(0)) rather than a priority queue and a hacky (start+end)%2 rotation-cost formula, making correctness fragile and over-modelled via the Step class. |
| online_2.py | 118 | 68.53 | B | 58 | +10.5 | #15:0, #17:0, #25:15 | Readable with named constants and a direction model, but duplicates two near-identical Dijkstras and pushes whole path-sets through the heap for Part 2, plus a hardcoded Windows input path. |
| synth_primitive.py | 73 | 53.17 | C | 48 | +5.2 | #12:0, #16:0, #25:0 | A correct, compact Dijkstra-plus-backtrack for both parts but with no structure, pervasive single-letter names, magic numbers, and redundant setdefault calls that hurt readability. |
| online_1.py | 51 | 93.55 | A | 28 | +65.5 | #25:0, #6:83, #1:85 | Wholesale copies the heapq-docs lazy-deletion PQ recipe it never needs, uses single-letter state, deeply nested inline conditionals with repeated index arithmetic and magic 1000000, and only solves Part 1. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.4** (n=5)

## 2024_q17

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 94 | 84.27 | A | 90 | -5.7 | #14:0, #25:0, #27:40 | Named opcode constants, typed frozen dataclasses, clear docstrings, and an elegant comprehension-based quine search make this the most readable and well-modelled solution, with only mild over-engineering from per-instruction immutable replacement. |
| synth_mid.py | 67 | 73.14 | B | 82 | -8.9 | #14:0, #25:0, #15:17 | A clean, well-decomposed simulator with sensible naming and explicit error handling for the reserved combo operand, plain but solid throughout. |
| online_1.py | 74 | 75.37 | B | 74 | +1.4 | #14:0, #25:0, #12:30 | A clear opcode-dispatch interpreter with helpful comments, but coupled to an external framework, a missing combo case 7, and a dense Part 2 documented via triple-quoted-string pseudo-comments hurt clarity. |
| tomek.py | 119 | 80.52 | A | 64 | +16.5 | #25:0, #16:2, #30:25 | Ambitious OOP modelling (Registers/Operand/Instruction/Program) but over-engineered and burdened by smells: float-based integer division, a recursive search mutating a shared set, module-level side effects, and an external dependency. |
| online_2.py | 60 | 88.75 | A | 52 | +36.8 | #25:0, #27:0, #24:50 | Clever but brittle: it hardcodes a transpiled version of the author's specific input rather than a general VM, shadows the builtin next, and only parses register A, making it fragile and poorly generalised despite a tidy reconstruction loop. |
| synth_primitive.py | 61 | 66.5 | B | 40 | +26.5 | #14:0, #25:0, #12:18 | Functionally correct and compact but with cryptic single-letter names (go, p2, x, y, v, o), no documentation, and crammed formatting that severely undermine readability. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.2** (n=6)

## 2024_q20

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 75 | 90.39 | A | 91 | -0.6 | #15:0, #25:20, #27:45 | Cleanly decomposed with type aliases, an explanatory docstring of the key insight, named constants, deque BFS, boundary error handling, and a proper main guard with CLI args. |
| tomek.py | 84 | 90.31 | A | 74 | +16.3 | #15:0, #27:0, #25:5 | Strong domain modelling via a RaceTrack class with helpers and explicit parse-error raising, slightly weakened by an awkwardly placed HTML-tagged comment, reliance on dict insertion order, and a convoluted min-over-neighbours BFS. |
| online_1.py | 75 | 78.27 | B | 62 | +16.3 | #16:0, #25:0, #15:17 | Readable names and a sensible offset-precompute approach, but cluttered by a dead/commented-out duplicate method, O(n) list-pop BFS, and fragile magic boundary checks. |
| online_2.py | 98 | 80.78 | A | 55 | +25.8 | #15:0, #17:0, #25:0 | Good direction/constant naming and a tidy generator, but over-engineered with unnecessary Dijkstra (two passes), a hardcoded Windows path, work running at import time with no main guard. |
| synth_primitive.py | 54 | 49.11 | D | 34 | +15.1 | #12:0, #16:0, #24:0 | Functionally minimal with single-letter names, no abstraction, copy-pasted part1/part2 loops, and O(n) list-pop BFS, offering almost no readability or structure. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.9** (n=5)

## 2024_q21

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 83 | 82.24 | A | 93 | -10.8 | #16:0, #25:0, #27:25 | Exemplary readability with type aliases, docstrings, and named pure functions; elegant two-candidate path generation avoids brute force, clean memoized recursion, and both parts handled via a proper main(). |
| tomek.py | 128 | 82.06 | A | 82 | +0.1 | #16:0, #25:0, #15:23 | Strong domain modelling with a PadType enum, descriptive names, an explanatory docstring, and scalable iterative memoization, marred only by some repetition, a hard external dependency, and generic Exception use. |
| online_2.py | 86 | 83.7 | A | 74 | +9.7 | #15:0, #16:0, #24:42 | Clean memoized class-based solution with reasonable naming, but reinvents itertools.product, uses a mutable default arg, duplicates setup across part1/part2 via side-effecting instance attributes, and packs dense gap logic into parse_moves. |
| synth_mid.py | 65 | 75.54 | B | 68 | +7.5 | #16:0, #25:0, #14:15 | Readable, well-commented, and well-named, but relies on permutation brute force and hardcodes three expansion levels with no memoization, so it only handles Part 1 and would not scale. |
| online_1.py | 266 | 65.7 | B | 35 | +30.7 | #16:0, #25:0, #30:0 | Severely over-engineered: hundreds of lines of unrelated animation/rendering code wrap a solver built on global mutable state and a confusing dual-mode (length-vs-string) design with near-duplicate functions and cryptic names. |
| synth_primitive.py | 68 | 71.63 | B | 28 | +43.6 | #14:0, #15:0, #25:0 | Cryptic single-letter names, no whitespace, a fragile order-picking heuristic, a gap check that fails to break, and Part-1-only scope with no memoization make it dense and hard to follow. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.771** (n=6)

## 2024_q22

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 60 | 85.5 | A | 92 | -6.5 | #25:0, #27:0, #24:25 | Cleanest overall: named constants, full type hints with a Sequence alias, focused single-purpose functions, docstrings, and proper parse/main separation, marred only slightly by a clumsy type:ignore comment. |
| online_1.py | 39 | 86.78 | A | 88 | -1.2 | #25:0, #27:0, #24:33 | Idiomatic and well-typed with strong domain naming, an elegant deque(maxlen=4) sliding window, and clean setdefault first-occurrence logic, though it embeds magic numbers and lacks an entrypoint. |
| tomek.py | 54 | 88.14 | A | 76 | +12.1 | #25:0, #27:0, #1:27 | Good domain modelling via explicit mix/prune/next_secret_number and descriptive names, but suffers from redundant intermediate variables, an awkward dict-of-sets keyed by index, hardcoded filenames, and module-level print side effects. |
| online_2.py | 49 | 81.28 | A | 58 | +23.3 | #15:0, #16:0, #25:0 | Reasonable logic but carries a large block of dead commented-out code, no type hints, duplicated evolution logic across both parts, and an untyped data parameter coupled to an external base class. |
| synth_primitive.py | 57 | 89.08 | A | 45 | +44.1 | #15:0, #25:0, #24:23 | A coherent MonkeyMarket class with a main entrypoint, but cramped single-letter names throughout, evolution logic duplicated inline across next/part1/part2, a manual max loop, and no type hints or error handling. |

Rank agreement (Spearman ρ, Moses vs Judge): **-0.4** (n=5)

## 2024_q24

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 109 | 94.82 | A | 90 | +4.8 | #15:0, #27:15, #1:54 | Clear module docstring, a focused frozen Gate dataclass with intention-revealing helper methods, well-decomposed pure functions, and explicit cycle-detection error handling make this the most readable and maintainable solution; the part-2 structural rules are documented inline. |
| online_1.py | 182 | 83.81 | A | 78 | +5.8 | #15:0, #11:4, #6:67 | Strong, precise type aliases and well-documented helpers show real domain modelling, but the recursive Wiring abstraction in part 2 is dense and hard to follow, and the local import plus deque bookkeeping add friction that pushes it below the cleaner dataclass approach. |
| tomek.py | 145 | 90.29 | A | 70 | +20.3 | #25:17, #27:42, #15:44 | A genuine Wire/Gate/Circuit object model with an explanatory ASCII-diagram docstring and readable structural checks, undercut by terse single-letter parsing in go(), an external main import dependency, exception-based control flow, and hardcoded bit-range loops with acknowledged unhandled edge cases. |
| online_2.py | 93 | 88.0 | A | 55 | +33.0 | #15:0, #25:0, #14:40 | Reasonably named functions and clean parsing, but part 2 is not a real solver (hardcoded input-specific swaps with a TODO) and modify_operations mutates loop variables and reuses names confusingly, hurting both correctness-of-intent clarity and structure. |
| synth_primitive.py | 36 | 60.58 | C | 22 | +38.6 | #12:0, #15:0, #25:0 | Solves only part 1 with cryptic one-letter names (d, w, g, l, x, p), no functions or abstraction beyond a single monolithic go(), magic done flags, and zero error handling or documentation. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.7** (n=5)

## 2024_q4

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 65 | 96.33 | A | 88 | +8.3 | #1:25, #21:50, #5:84 | Clean domain modelling with Point/Grid abstractions, a generic spells_word helper, type hints and tidy part decomposition; only mildly over-engineered for the problem size. |
| synth_mid.py | 40 | 93.32 | A | 82 | +11.3 | #14:35, #1:36, #24:80 | Idiomatic, simple and readable with well-named helpers (in_bounds, count_xmas/count_x_mas) and clear direction handling, hitting the sweet spot of clarity without ceremony. |
| online_2.py | 37 | 85.94 | A | 70 | +15.9 | #15:0, #21:50, #14:52 | Sound diagonal-bucketing approach with helpful comments and a fine part2, but the verbose diagonal dict-building and the opaque _set name hold it back. |
| online_1.py | 39 | 93.37 | A | 64 | +29.4 | #25:0, #1:56, #3:100 | Compact and clever numpy/regex solution with rare file-error handling, but inconsistent 1/2-space indentation, terse lambdas and isSM naming make it cryptic to read. |
| synth_primitive.py | 37 | 63.17 | C | 38 | +25.2 | #12:0, #14:0, #24:33 | Functionally correct but a single monolithic solve() with module-level I/O, single-letter names and both parts crammed into one deeply nested loop, with no decomposition. |
| tomek.py | 79 | 76.19 | B | 30 | +46.2 | #16:0, #25:0, #14:0 | Over-engineered yet incomplete: a confusing transpose/flip in read_grid inverts coordinate semantics, per-direction hardcoded offset lists duplicate heavily, it imports from a nonexistent module, and main runs only part2 leaving part1 dead. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.771** (n=6)

## 2024_q6

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 87 | 96.24 | A | 92 | +4.2 | #1:36, #24:69, #14:75 | Idiomatic frozen-dataclass domain model with elegant rotation math, clear docstrings, proper ValueError, and clean part1/part2/main decomposition; only minor blemishes are a bare open() and the unused open_cells method. |
| tomek.py | 155 | 84.4 | A | 80 | +4.4 | #30:0, #1:46, #15:55 | Rich, well-named domain model (Direction/Coordinates/Guard/Lab) with full dunder methods and good readability, but verges on over-engineered with an if/elif direction chain instead of deltas, confusing width/height naming, and generic Exception usage. |
| online_1.py | 43 | 77.55 | B | 78 | -0.5 | #15:0, #25:0, #30:0 | Compact and elegant, leveraging shared grid utilities and a cycle-based offset trick with a clean single track_guard function, though the empty-set loop sentinel is slightly awkward and it leans heavily on external framework scaffolding. |
| online_2.py | 55 | 93.06 | A | 60 | +33.1 | #15:0, #14:54, #1:55 | Sensibly decomposed into methods with a clever (if hacky) json round-trip copy, but terse names (_map, n, d, vi/vj), the subtle entry-point loop-detection logic, and falsy default-arg handling for idx hurt clarity. |
| synth_primitive.py | 77 | 44.28 | D | 18 | +26.3 | #12:0, #14:0, #16:0 | Single-letter naming throughout, one monolithic function with the entire walk loop duplicated between parts, zero abstraction, comments, or error handling — minimally readable and unmaintainable. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.7** (n=5)

## 2024_q8

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 72 | 91.91 | A | 92 | -0.1 | #21:0, #1:29, #24:71 | Excellent domain modelling with Point/Grid dataclasses and operator-based vector arithmetic, a clean strategy-function abstraction unifying both parts, full type hints and clear docstrings, with only mild risk of being slightly heavier than the task strictly needs. |
| synth_mid.py | 36 | 87.25 | A | 84 | +3.2 | #25:44, #1:45, #14:52 | Highly readable procedural solution with clear naming, a single cohesive solve that computes both parts via combinations and a small in_bounds helper, and good comments, lacking only explicit domain types. |
| online_2.py | 40 | 68.81 | B | 76 | -7.2 | #16:0, #12:6, #14:25 | Clean vector-arithmetic approach with defaultdict and combinations, but part1/part2 fully duplicate parsing and setup and the underscore-prefixed local names (_map, _idx, _dir) are unidiomatic. |
| synth_primitive.py | 43 | 68.49 | B | 52 | +16.5 | #12:0, #15:0, #14:25 | Correct and compact logic but crippled by single-letter naming throughout (g, h, w, d, s1, s2) and a redundant ordered-pair double loop with an i==j skip, hurting readability and clarity. |
| tomek.py | 96 | 86.26 | A | 48 | +38.3 | #30:0, #1:30, #15:67 | Has real domain types (Coordinates/Antenna) yet suffers from confusing resonance stepping recomputed from the origin, module-level execution side effects, an external read_input dependency, and an over-strict exception on single-antenna frequencies. |
| online_1.py | 112 | 65.22 | B | 28 | +37.2 | #14:0, #15:0, #16:0 | Severely over-engineered with massive duplicated four-way directional branching, pervasive blank-line noise and typos, side-effecting map mutation, a single bound used for both dimensions, and a bare except that silently swallows errors. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.829** (n=6)

## 2024_q9

| Solution | LOC | Moses | Grade | Judge | Gap | Weakest rules | Justification |
|---|---|---|---|---|---|---|---|
| synth_clean.py | 88 | 94.72 | A | 90 | +4.7 | #27:11, #15:38, #25:55 | Clean per-block model with a FREE sentinel, small single-purpose functions each documented, full type hints, and a proper main guard make this the most readable and well-decomposed solution. |
| online_2.py | 68 | 82.95 | A | 72 | +11.0 | #15:0, #25:0, #30:0 | Idiomatic and well-typed with a tidy Item dataclass and expand/parse helpers, but the two separately-redefined Solution classes, duplicated imports, and subtle list insert/mutate logic in part 2 reduce clarity. |
| online_1.py | 108 | 76.65 | B | 60 | +16.7 | #15:0, #27:0, #12:19 | A reasonable Block abstraction with decent naming, but it conflates file lists, type flags, and space lengths into one struct and relies on try/except as control flow, making the stateful compaction hard to follow. |
| tomek.py | 105 | 86.16 | A | 52 | +34.2 | #15:0, #30:0, #14:59 | Helpful worked-example comments and an explicit FileBlock type, but redundant per-block file_length storage, tangled nested loops in compact_contiguous, and leftover debug prints undercut it. |
| synth_primitive.py | 70 | 58.89 | C | 28 | +30.9 | #12:0, #15:0, #24:0 | A single monolithic function with pervasive one-letter names (d, f, l, r, m, st, ln), no types, no docstrings, and inlined part1/part2 logic makes it correct but very hard to read or maintain. |

Rank agreement (Spearman ρ, Moses vs Judge): **0.7** (n=5)

## Summary

| Question | Spearman ρ | n |
|---|---|---|
| 2022_q11 | 0.7 | 5 |
| 2022_q2 | 0.8 | 5 |
| 2022_q8 | 0.829 | 6 |
| 2023_q1 | 0.7 | 5 |
| 2023_q11 | 0.9 | 5 |
| 2023_q2 | 0.7 | 5 |
| 2023_q3 | 0.9 | 5 |
| 2023_q5 | 0.8 | 5 |
| 2023_q7 | 0.943 | 6 |
| 2024_q10 | 0.6 | 6 |
| 2024_q12 | 0.7 | 5 |
| 2024_q13 | 0.9 | 5 |
| 2024_q14 | 0.771 | 6 |
| 2024_q15 | 0.371 | 6 |
| 2024_q16 | 0.4 | 5 |
| 2024_q17 | 0.2 | 6 |
| 2024_q20 | 0.9 | 5 |
| 2024_q21 | 0.771 | 6 |
| 2024_q22 | -0.4 | 5 |
| 2024_q24 | 0.7 | 5 |
| 2024_q4 | 0.771 | 6 |
| 2024_q6 | 0.7 | 5 |
| 2024_q8 | 0.829 | 6 |
| 2024_q9 | 0.7 | 5 |
