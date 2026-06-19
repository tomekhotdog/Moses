# Commandment 21: Cohesive classes

## Summary
A cohesive class's methods share state. LCOM4 counts disconnected method clusters; more than one suggests the class should split.


## Target Shape
Every method touches a common core of fields.


## Violation Shape
Method groups that use entirely separate fields (a god class).


## Anti Patterns
- A "Manager"/"Utils" class bundling unrelated responsibilities.

## Interactions
Splitting raises composition (#29) and lowers class complexity (#31).

---
*Weight 2 · Martin (LCOM); GoF · implemented*
