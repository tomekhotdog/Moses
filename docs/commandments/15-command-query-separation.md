# Commandment 15: Command-query separation

## Summary
A method should either change state (a command) or return a value (a query), not both. Mixing the two hides side effects.


## Target Shape
Queries are pure; commands return None (or only a status).


## Violation Shape
A method that mutates `self`/arguments AND returns a meaningful value.


## Anti Patterns
- A pop()-style method proliferating where purity is expected.

## Interactions
Supports immutability (#24) and testability (#20).

---
*Weight 2 · Meyer; Martin · implemented*
