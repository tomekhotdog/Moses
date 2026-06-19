# Commandment 20: Mutation kill rate

## Summary
Mutation testing measures whether your tests actually catch injected bugs. A high kill rate means strong assertions. Opt-in (slow); enable with --deep.


## Target Shape
Tests that fail when behaviour changes; few surviving mutants.


## Violation Shape
Mutants that survive because assertions are weak or missing.


## Anti Patterns
- Tests that exercise code without asserting outcomes.

## Interactions
Reinforced by command-query separation (#15) and small functions (#11).

---
*Weight 5 · Mutation testing literature · implemented*
