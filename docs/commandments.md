# The 31 Commandments

Each Commandment has a stable number, a Weight (all Weights sum to 100), a source attribution, and a status: **implemented** rules are measured by the scorer; the rest default to `not_measured` and never affect the Score until implemented.

| # | Commandment | Weight | Source | Status |
|---|-------------|--------|--------|--------|
| 1 | Deep modules | 8 | Ousterhout, APoSD ch.4 | implemented |
| 2 | Loose coupling | 5 | Ousterhout; GoF | implemented |
| 3 | No pass-through methods | 2 | Ousterhout, APoSD ch.7 | implemented |
| 4 | Layers add abstraction | 3 | Ousterhout, APoSD ch.7 | planned |
| 5 | Pull complexity downward | 3 | Ousterhout, APoSD ch.8 | implemented |
| 6 | Define errors out of existence | 3 | Ousterhout, APoSD ch.10 | implemented |
| 7 | Comment where complexity demands it | 2 | Ousterhout; McConnell | planned |
| 8 | Strategic over tactical | 4 | Ousterhout, APoSD ch.3 | planned |
| 9 | Meaningful names | 4 | Martin, Clean Code ch.2 | planned |
| 10 | One name per concept | 2 | Martin, Clean Code ch.2 | planned |
| 11 | Small functions | 2 | Martin, Clean Code ch.3 | implemented |
| 12 | Low cognitive complexity | 6 | SonarSource; McConnell | implemented |
| 13 | Few parameters | 4 | Martin, Clean Code ch.3 | implemented |
| 14 | Shallow nesting | 2 | McConnell, Code Complete ch.19 | implemented |
| 15 | Command-query separation | 2 | Meyer; Martin | implemented |
| 16 | DRY | 6 | Hunt & Thomas; Martin | implemented |
| 17 | No commented-out code | 1 | Martin, Clean Code ch.4 | implemented |
| 18 | No empty catch blocks | 2 | McConnell; Martin | implemented |
| 19 | Test isolation | 3 | Martin, Clean Code ch.9 | planned |
| 20 | Mutation kill rate | 5 | Mutation testing literature | implemented |
| 21 | Cohesive classes | 2 | Martin (LCOM); GoF | implemented |
| 22 | Law of Demeter | 3 | Lieberherr; Martin | implemented |
| 23 | Narrow variable scope | 2 | McConnell, Code Complete ch.10 | implemented |
| 24 | Prefer immutability | 3 | Effective Java; FP practice | implemented |
| 25 | No magic numbers | 2 | Martin; McConnell | implemented |
| 26 | Validate at boundaries | 3 | Ousterhout; defensive programming | planned |
| 27 | Data over primitives | 3 | Fowler, primitive obsession | planned |
| 28 | Program to interfaces | 4 | GoF; DIP | planned |
| 29 | Composition over inheritance | 3 | GoF, Design Patterns | implemented |
| 30 | Pattern parsimony | 3 | GoF; Ousterhout | planned |
| 31 | Contain class complexity | 3 | Martin (WMC); McConnell | implemented |

Weights sum to **100**. The MVP enabled-set is [1, 2, 3, 5, 6, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 29, 31] (#20 only runs under `--deep`).

---

## 1. Deep modules

*Weight 8 — Ousterhout, APoSD ch.4 — implemented*

A good module hides a lot of implementation behind a small interface. Depth = implementation LOC / API surface. Shallow modules leak complexity onto their callers.

**Violation shape:** Many tiny public functions that merely expose internals, or wide signatures that force callers to understand the implementation.

## 2. Loose coupling

*Weight 5 — Ousterhout; GoF — implemented*

Minimise how many distinct external names a class depends on (a proxy for Coupling Between Objects). Lower coupling means changes stay local.

**Violation shape:** A class that references many imported modules/classes directly.

## 3. No pass-through methods

*Weight 2 — Ousterhout, APoSD ch.7 — implemented*

A pass-through method does nothing but forward its arguments to another method with essentially the same signature. It adds indirection, not value.

**Violation shape:** `def f(self, x): return self.other(x)` or `def f(self, x): return obj.g(x)`.

## 4. Layers add abstraction

*Weight 3 — Ousterhout, APoSD ch.7 — planned*

Layers add abstraction

## 5. Pull complexity downward

*Weight 3 — Ousterhout, APoSD ch.8 — implemented*

It is better for a module to absorb complexity than to expose it. Required parameters with no sensible default push complexity onto every caller.

**Violation shape:** Functions with many required positional parameters and no defaults.

## 6. Define errors out of existence

*Weight 3 — Ousterhout, APoSD ch.10 — implemented*

The best error handling is an API shaped so the error cannot arise. Prefer designs that make invalid states unrepresentable over defensive raising.

**Violation shape:** A high density of `raise` statements relative to the code that could instead have been designed to avoid the condition.

## 7. Comment where complexity demands it

*Weight 2 — Ousterhout; McConnell — planned*

Comment where complexity demands it

## 8. Strategic over tactical

*Weight 4 — Ousterhout, APoSD ch.3 — planned*

Strategic over tactical

## 9. Meaningful names

*Weight 4 — Martin, Clean Code ch.2 — planned*

Meaningful names

## 10. One name per concept

*Weight 2 — Martin, Clean Code ch.2 — planned*

One name per concept

## 11. Small functions

*Weight 2 — Martin, Clean Code ch.3 — implemented*

Functions should be short enough to hold in your head. The p95 length across the codebase should stay modest.

**Violation shape:** Functions of 50+ non-blank lines doing several things.

## 12. Low cognitive complexity

*Weight 6 — SonarSource; McConnell — implemented*

Cognitive complexity (SonarSource) and cyclomatic complexity both measure how hard a function is to follow. Keep both low.

**Violation shape:** Nested conditionals, loops with embedded branches, boolean thickets.

## 13. Few parameters

*Weight 4 — Martin, Clean Code ch.3 — implemented*

Long parameter lists are hard to call correctly. Bundle related parameters into a value object.

**Violation shape:** Signatures with five or more parameters.

## 14. Shallow nesting

*Weight 2 — McConnell, Code Complete ch.19 — implemented*

Deeply indented code is hard to read. Keep nesting shallow with guard clauses and early returns.

**Violation shape:** Four-plus levels of nested if/for/while/with/try.

## 15. Command-query separation

*Weight 2 — Meyer; Martin — implemented*

A method should either change state (a command) or return a value (a query), not both. Mixing the two hides side effects.

**Violation shape:** A method that mutates `self`/arguments AND returns a meaningful value.

## 16. DRY

*Weight 6 — Hunt & Thomas; Martin — implemented*

Duplicated logic is a maintenance hazard. Detect repeated token blocks and extract them.

**Violation shape:** Copy-pasted blocks differing only in a literal or a name.

## 17. No commented-out code

*Weight 1 — Martin, Clean Code ch.4 — implemented*

Commented-out code rots and confuses. Delete it; version control remembers.

**Violation shape:** Runs of comment lines that parse as Python.

## 18. No empty catch blocks

*Weight 2 — McConnell; Martin — implemented*

Swallowing exceptions hides failures. Every handler should do something meaningful.

**Violation shape:** `except ...: pass` (or a bare `...`) with no handling.

## 19. Test isolation

*Weight 3 — Martin, Clean Code ch.9 — planned*

Test isolation

## 20. Mutation kill rate

*Weight 5 — Mutation testing literature — implemented*

Mutation testing measures whether your tests actually catch injected bugs. A high kill rate means strong assertions. Opt-in (slow); enable with --deep.

**Violation shape:** Mutants that survive because assertions are weak or missing.

## 21. Cohesive classes

*Weight 2 — Martin (LCOM); GoF — implemented*

A cohesive class's methods share state. LCOM4 counts disconnected method clusters; more than one suggests the class should split.

**Violation shape:** Method groups that use entirely separate fields (a god class).

## 22. Law of Demeter

*Weight 3 — Lieberherr; Martin — implemented*

Talk only to immediate collaborators. Long attribute chains couple you to the internals of distant objects.

**Violation shape:** Call sites reaching through two or more intermediate attributes.

## 23. Narrow variable scope

*Weight 2 — McConnell, Code Complete ch.10 — implemented*

Declare variables close to first use and keep their live range short, so the reader holds less in mind.

**Violation shape:** Variables declared at the top of a long function, used much later.

## 24. Prefer immutability

*Weight 3 — Effective Java; FP practice — implemented*

Immutable data is easier to reason about. Avoid reassigning locals and mutating shared structures.

**Violation shape:** Locals reassigned many times; in-place mutation of arguments.

## 25. No magic numbers

*Weight 2 — Martin; McConnell — implemented*

Unexplained numeric literals obscure intent. Name them.

**Violation shape:** Bare literals like 86400, 7777, 0.7 sprinkled through logic.

## 26. Validate at boundaries

*Weight 3 — Ousterhout; defensive programming — planned*

Validate at boundaries

## 27. Data over primitives

*Weight 3 — Fowler, primitive obsession — planned*

Data over primitives

## 28. Program to interfaces

*Weight 4 — GoF; DIP — planned*

Program to interfaces

## 29. Composition over inheritance

*Weight 3 — GoF, Design Patterns — implemented*

Deep inheritance hierarchies are rigid and fragile. Prefer composing behaviour from collaborators.

**Violation shape:** Chains like Base -> Middle -> Deep -> Deeper.

## 30. Pattern parsimony

*Weight 3 — GoF; Ousterhout — planned*

Pattern parsimony

## 31. Contain class complexity

*Weight 3 — Martin (WMC); McConnell — implemented*

Weighted Methods per Class (sum of method complexities) should stay bounded; a high WMC means the class does too much.

**Violation shape:** A class whose methods are individually and collectively complex.

