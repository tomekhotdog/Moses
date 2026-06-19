# Commandment 25: No magic numbers

## Summary
Unexplained numeric literals obscure intent. Name them.


## Target Shape
Named constants with meaningful names; 0 and 1 are exempt.


## Violation Shape
Bare literals like 86400, 7777, 0.7 sprinkled through logic.


## Anti Patterns
- Repeated literals that should be one named constant.

## Interactions
Often co-occurs with DRY (#16).

---
*Weight 2 · Martin; McConnell · implemented*
