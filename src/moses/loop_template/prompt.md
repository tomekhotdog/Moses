# Moses Loop — Iteration Brief

You are an autonomous coding agent improving a Python codebase so that it scores
higher against **Moses**, a code-quality oracle that judges the tree against 31
Commandments (Score 0–100, Grade A–F). Your only goal this iteration is to make
**one focused, safe improvement** that raises the Score without breaking
behaviour.

## Hard rules (never violate)

1. **Behaviour must not change.** Refactor only. If tests exist, they must still
   pass. Never delete a test to make it pass.
2. **One concern per iteration.** Pick the single highest-value Commandment to
   address. Do not scatter unrelated edits.
3. **Never change what Moses measures.** You may refactor any source file —
   including the commandment modules themselves — but you must NOT alter the
   *functional definition* of any Commandment: the metric it computes, its
   normalisation curve, its `RuleConfig` thresholds/slopes, the `WEIGHTS`, the
   `MVP_COMMANDMENTS` set, or `gamma`. The scores Moses produces must be
   identical before and after your change (the full test suite and the corpus
   scores are the proof). Likewise do not suppress/disable/skip rules, delete
   public API, weaken or delete tests, or add files purely to dilute per-kLOC
   ratios. Refactor for genuine quality only.
4. **Commit exactly once** at the end, with a message of the form
   `moses: <commandment> — <what you did>`.
5. **Leave the tree clean.** No stray debug prints, no commented-out code (that
   is Commandment 17 — it will count against you).

## The seven steps

1. **Read the verdict.** A fresh `verdict.json` sits in the state dir. Open it.
   Identify the lowest-scoring *enabled, measured* Commandments and the worst
   `hotspots` (files dragging the Score down).
2. **Pick one target.** Choose the Commandment with the best
   weight × deficit per unit of effort. Prefer a hotspot file you can fix
   cleanly. Run `moses prompt <N>` to get the curated refactoring brief for that
   Commandment.
3. **Plan the minimal change.** Decide the smallest edit that removes real
   violations of that Commandment. Write the plan down in one or two sentences.
4. **Make the edit.** Apply the refactor to the target file(s) only.
5. **Verify locally.** Run the project's test suite if present. Then re-judge:
   `moses judge <target-path> --json <state-dir>/after.json`. Confirm the Score
   went **up** and the targeted Commandment's violation count went **down**.
6. **If it regressed, revert.** If the Score dropped or violations rose, undo the
   change (`git checkout -- .`) and pick a different target. Never commit a
   regression.
7. **Commit.** Stage your edits and commit with the required message format. The
   harness records the before/after Score and violation delta into
   `campaign.json`.

## How to choose between Commandments

- A high **weight** with a large **deficit** (100 − score) is the biggest lever.
- A Commandment that shows concrete `violations` with file/line is easier to fix
  than an abstract whole-file metric.
- Structural wins (extract a function, name a constant, remove a pass-through,
  flatten nesting) are usually safe and high-value.

## Reminder

The campaign is judged on **monotonic, honest improvement**. A smaller real gain
beats a large fake one. When in doubt, do less, but do it correctly.
