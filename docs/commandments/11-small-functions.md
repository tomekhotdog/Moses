# Commandment 11: Small functions

## Summary
Functions should be short enough to hold in your head. The p95 length across the codebase should stay modest.


## Target Shape
Most functions well under ~30 lines; the longest are still comprehensible.


## Violation Shape
Functions of 50+ non-blank lines doing several things.


## Anti Patterns
- One mega-function with sequential phases that should be named helpers.

## Interactions
Splitting long functions usually lowers cognitive complexity (#12) and nesting (#14).

---
*Weight 2 · Martin, Clean Code ch.3 · implemented*
