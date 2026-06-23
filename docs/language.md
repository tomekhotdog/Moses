# Canonical Language

Moses uses a small, fixed vocabulary. These terms are PascalCase domain nouns;
use them consistently in code, docs, and reports.

| Term | Meaning |
|------|---------|
| **Commandment** | One of the 31 rules. Identified by a stable number 1–31. |
| **Score** | The overall quality measure in [0, 100]. |
| **ScoreContribution** | A single Commandment's per-rule score in [0, 100]. |
| **Grade** | The letter A–F derived from the Score. |
| **Metric** | The raw measured quantity for a Commandment before normalisation (e.g. p95 LOC, mean chain depth). |
| **Normalisation** | The curve mapping a Metric to a ScoreContribution. |
| **Weight** | The integer importance of a Commandment; all Weights sum to 100. |
| **Verdict** | The full result object: Score, Grade, per-Commandment results, Hotspots, overview, meta. |
| **Hotspot** | A file ranked by how much it drags the Score down. |
| **Codebase** | The loaded source tree: a root plus a list of SourceFiles. |
| **SourceFile** | One Python file with its text and derived line counts. |
| **Loop** | An autonomous improvement campaign (the RALPH harness). |
| **Iteration** | One pass of the Loop: judge → improve → verify → commit → record. |
| **Campaign** | The whole Loop run, recorded in `campaign.json`. |
| **Concept** | A domain type — a class, `NewType`, `Enum`, dataclass/`NamedTuple`, or known value type (`datetime`, `Decimal`, `UUID`, `Path`) — as opposed to a raw primitive. C27 rewards expressing the public surface in Concepts. |
| **Primitive** | A raw built-in scalar/container that carries no domain meaning: `str`/`int`/`float`/`bool`/`bytes`/`None`, `Any`, and unparameterized `dict`/`list`/`tuple`. |
| **Slot** | An annotated point on the public type surface that C27 scores: a parameter, a return annotation, or a class attribute. |
| **DomainSurfaceRatio** | C27's Metric: the mean domain-richness (`Concept` = 1, weak = 0.5, `Primitive` = 0) across qualifying Slots. |

## Calibration vocabulary

| Term | Meaning |
|------|---------|
| **Corpus** | The labelled set of Advent-of-Code solutions used to calibrate rules. Lives under `evals/corpus/`; 2024 trains, 2022/23 tests. |
| **Judge** | The LLM-as-judge: a holistic code-quality % (0–100) with justification, assigned independently of Moses. The proxy for "the Truth". |
| **Comparison** | The single file (`evals/corpus/comparison.md`, backed by `comparison.json`) laying each solution's Moses Score beside its Judge score. |
| **Calibration** | Tuning rule parameters (weights, curves, thresholds) until the Moses Score tracks the Judge score across the Corpus. (Phase 2.) |

## Status vocabulary

A `CommandmentResult.status` is exactly one of: `measured`, `not_measured`,
`error`, `skipped`. See `spec.md` for semantics.

## Spelling

The codebase uses British spelling for "Normalisation" but otherwise follows the
authors' original terminology (e.g. "Law of Demeter", "command-query
separation", "cognitive complexity").
