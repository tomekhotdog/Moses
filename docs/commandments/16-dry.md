# Commandment 16: DRY

## Summary
Duplicated logic is a maintenance hazard. Detect repeated token blocks and extract them.


## Target Shape
Each non-trivial piece of logic exists in exactly one place.


## Violation Shape
Copy-pasted blocks differing only in a literal or a name.


## Anti Patterns
- Two functions that are 90% identical.

## Interactions
Extraction often creates deep helpers (#1) and shrinks functions (#11).

---
*Weight 6 · Hunt & Thomas; Martin · implemented*
