# Commandment 17: No commented-out code

## Summary
Commented-out code rots and confuses. Delete it; version control remembers.


## Target Shape
Comments explain intent, never preserve dead code.


## Violation Shape
Runs of comment lines that parse as Python.


## Anti Patterns
- A '# old_value = compute(...)' line left behind after a change.

## Interactions
Independent; cheap to fix and always safe.

---
*Weight 1 · Martin, Clean Code ch.4 · implemented*
