# Commandment 13: Few parameters

## Summary
Long parameter lists are hard to call correctly. Bundle related parameters into a value object.


## Target Shape
Functions with roughly three or fewer parameters.


## Violation Shape
Signatures with five or more parameters.


## Anti Patterns
- Passing a struct's fields individually instead of the struct.
- Boolean flag parameters that select behaviour.

## Interactions
Pairs with #27 (data over primitives) and #5 (pull complexity down).

---
*Weight 4 · Martin, Clean Code ch.3 · implemented*
