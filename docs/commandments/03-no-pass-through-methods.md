# Commandment 3: No pass-through methods

## Summary
A pass-through method does nothing but forward its arguments to another method with essentially the same signature. It adds indirection, not value.


## Target Shape
Methods either add real behaviour or are removed in favour of calling the delegate directly.


## Violation Shape
`def f(self, x): return self.other(x)` or `def f(self, x): return obj.g(x)`.


## Anti Patterns
- Wrapper classes that mirror another class method-for-method.
- Facades that forward every call unchanged.

## Interactions
Removing pass-throughs deepens modules (#1) and can reduce class complexity (#31).

---
*Weight 2 · Ousterhout, APoSD ch.7 · implemented*
