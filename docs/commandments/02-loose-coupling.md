# Commandment 2: Loose coupling

## Summary
Minimise how many distinct external names a class depends on (a proxy for Coupling Between Objects). Lower coupling means changes stay local.


## Target Shape
A class that talks to a handful of collaborators through narrow interfaces.


## Violation Shape
A class that references many imported modules/classes directly.


## Anti Patterns
- Reaching into global singletons everywhere.
- Instantiating many concrete collaborators inside one class.

## Interactions
Works with #28 (program to interfaces) and #22 (Law of Demeter).

---
*Weight 5 · Ousterhout; GoF · implemented*
