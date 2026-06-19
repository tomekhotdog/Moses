# Commandment 31: Contain class complexity

## Summary
Weighted Methods per Class (sum of method complexities) should stay bounded; a high WMC means the class does too much.


## Target Shape
Classes with a modest number of simple methods.


## Violation Shape
A class whose methods are individually and collectively complex.


## Anti Patterns
- God classes accreting responsibilities over time.

## Interactions
Lowered by extracting collaborators (#29) and improving cohesion (#21).

---
*Weight 3 · Martin (WMC); McConnell · implemented*
