# Commandment 1: Deep modules

## Summary
A good module hides a lot of implementation behind a small interface. Depth = implementation LOC / API surface. Shallow modules leak complexity onto their callers.


## Target Shape
Few public functions/methods, each with few parameters, backed by substantial, well-encapsulated implementation.


## Violation Shape
Many tiny public functions that merely expose internals, or wide signatures that force callers to understand the implementation.


## Anti Patterns
- Pass-through getters/setters that add no abstraction.
- Utility modules that are a flat list of unrelated public helpers.
- Public functions that take a dozen flags to steer behaviour.

## Interactions
Tightly linked to #3 (pass-through) and #13 (few parameters); fixing those usually deepens modules.

---
*Weight 8 · Ousterhout, APoSD ch.4 · implemented*
