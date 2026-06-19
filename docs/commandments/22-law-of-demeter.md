# Commandment 22: Law of Demeter

## Summary
Talk only to immediate collaborators. Long attribute chains couple you to the internals of distant objects.


## Target Shape
`a.do()` rather than `a.b.c.d.do()`.


## Violation Shape
Call sites reaching through two or more intermediate attributes.


## Anti Patterns
- obj.engine.config.settings.flags.read()

## Interactions
Lowering chains reduces coupling (#2).

---
*Weight 3 · Lieberherr; Martin · implemented*
