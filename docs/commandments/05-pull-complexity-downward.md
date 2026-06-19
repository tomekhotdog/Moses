# Commandment 5: Pull complexity downward

## Summary
It is better for a module to absorb complexity than to expose it. Required parameters with no sensible default push complexity onto every caller.


## Target Shape
Functions provide reasonable defaults; callers supply only what is unusual.


## Violation Shape
Functions with many required positional parameters and no defaults.


## Anti Patterns
- Configuration that must be fully specified at every call site.

## Interactions
Closely tied to #13 (few parameters) and #1 (deep modules).

---
*Weight 3 · Ousterhout, APoSD ch.8 · implemented*
