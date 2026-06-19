# Commandment 12: Low cognitive complexity

## Summary
Cognitive complexity (SonarSource) and cyclomatic complexity both measure how hard a function is to follow. Keep both low.


## Target Shape
Linear, flat control flow with early returns instead of deep branching.


## Violation Shape
Nested conditionals, loops with embedded branches, boolean thickets.


## Anti Patterns
- Deeply nested if/else ladders.
- Long boolean expressions combining many conditions.

## Interactions
Improves with #14 (shallow nesting) and #11 (small functions).

---
*Weight 6 · SonarSource; McConnell · implemented*
