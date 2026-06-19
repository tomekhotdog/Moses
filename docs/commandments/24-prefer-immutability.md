# Commandment 24: Prefer immutability

## Summary
Immutable data is easier to reason about. Avoid reassigning locals and mutating shared structures.


## Target Shape
Single-assignment locals; frozen value objects.


## Violation Shape
Locals reassigned many times; in-place mutation of arguments.


## Anti Patterns
- Accumulator reassignment where a comprehension would do.

## Interactions
Supports command-query separation (#15).

---
*Weight 3 · Effective Java; FP practice · implemented*
