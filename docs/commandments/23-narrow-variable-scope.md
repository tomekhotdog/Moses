# Commandment 23: Narrow variable scope

## Summary
Declare variables close to first use and keep their live range short, so the reader holds less in mind.


## Target Shape
Locals introduced just before use; small span between first and last use.


## Violation Shape
Variables declared at the top of a long function, used much later.


## Anti Patterns
- C-style "declare everything up front".

## Interactions
Improves with small functions (#11) and immutability (#24).

---
*Weight 2 · McConnell, Code Complete ch.10 · implemented*
