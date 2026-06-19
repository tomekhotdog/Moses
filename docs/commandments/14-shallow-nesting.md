# Commandment 14: Shallow nesting

## Summary
Deeply indented code is hard to read. Keep nesting shallow with guard clauses and early returns.


## Target Shape
Maximum block depth of about three.


## Violation Shape
Four-plus levels of nested if/for/while/with/try.


## Anti Patterns
- Arrow-shaped code that marches to the right and back.

## Interactions
Directly lowers cognitive complexity (#12).

---
*Weight 2 · McConnell, Code Complete ch.19 · implemented*
