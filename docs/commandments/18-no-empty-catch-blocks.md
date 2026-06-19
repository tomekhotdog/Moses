# Commandment 18: No empty catch blocks

## Summary
Swallowing exceptions hides failures. Every handler should do something meaningful.


## Target Shape
Handlers log, recover, or re-raise with context.


## Violation Shape
`except ...: pass` (or a bare `...`) with no handling.


## Anti Patterns
- {'Broad `except Exception': 'pass` around large blocks.'}

## Interactions
Relates to #6 (define errors away) — prefer designs that avoid the throw.

---
*Weight 2 · McConnell; Martin · implemented*
