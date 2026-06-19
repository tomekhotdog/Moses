# Commandment 6: Define errors out of existence

## Summary
The best error handling is an API shaped so the error cannot arise. Prefer designs that make invalid states unrepresentable over defensive raising.


## Target Shape
Total functions; empty/None handled by returning a neutral value where it is semantically correct.


## Violation Shape
A high density of `raise` statements relative to the code that could instead have been designed to avoid the condition.


## Anti Patterns
- Throwing on empty input where an empty result is the natural answer.

## Interactions
Balanced against #26 (validate at boundaries); validate at the edge, design errors away on the inside.

---
*Weight 3 · Ousterhout, APoSD ch.10 · implemented*
