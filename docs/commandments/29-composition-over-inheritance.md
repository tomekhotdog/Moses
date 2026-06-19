# Commandment 29: Composition over inheritance

## Summary
Deep inheritance hierarchies are rigid and fragile. Prefer composing behaviour from collaborators.


## Target Shape
Shallow hierarchies (depth <= 2); behaviour injected, not inherited.


## Violation Shape
Chains like Base -> Middle -> Deep -> Deeper.


## Anti Patterns
- Subclassing to reuse a method instead of delegating.

## Interactions
Pairs with #28 (program to interfaces) and #21 (cohesion).

---
*Weight 3 · GoF, Design Patterns · implemented*
