# Lessons

Practical notes accumulated while building and running Moses. These are the
non-obvious things worth remembering.

## Scoring design

- **Average over enabled, measured rules only.** Never let a disabled or
  unmeasured rule contribute a free 100 — that would let anyone inflate the
  Score by turning rules off. Both the numerator and denominator must exclude it.
- **Small codebases distort per-kLOC and percentile metrics.** A 30-line file
  with one magic number scores terribly on a per-1000-LOC curve. Tests on tiny
  fixtures should compare *relative* metrics (bad worse than good) rather than
  absolute thresholds.
- **Some metrics are not monotonic across "good" and "bad" fixtures.** Deep
  modules (#1) rewards lots of implementation behind little API, so a large messy
  file can legitimately out-score a tiny clean one. Don't force every rule into a
  "bad < good" test; assert on the behaviour the rule actually measures.

## Rule implementation

- **[decision] Rules cannot read `Config`.** The engine calls
  `cmd.evaluate(codebase)` flat (`engine.py:118`) — no config is passed. #20 even
  uses `shutil.which("mutmut")` rather than `config.mutmut_path`, so
  `mutmut_path`/`jscpd_path` are dead fields. A rule needing a tunable (e.g. C27's
  target ratio) ships it as a module-level constant; per-project config awaits a
  deliberate config-threading refactor of the rule protocol. Don't thread config
  into one rule ad hoc.

- **A pass-through (#3) must delegate to a *method* and forward its args.**
  `return sum(x for x in items)` is not a pass-through (it's a builtin call doing
  real work); `return self.add_item(value)` is. Gate on `ast.Attribute` call
  targets and reject generator/keyword/computed arguments.
- **Commented-out-code (#17) detection must skip prose headers.** Dead code is
  often preceded by a human comment that won't parse. Scan each comment run for
  the largest contiguous sub-block that parses as Python, rather than requiring
  the whole run to parse.
- **Law of Demeter (#22) measures *call* chains, not attribute chains.** A long
  `a.b.c.d` access that never calls anything isn't what the rule detects; the
  violation shape is `a.b.c.d.method()`. Fixtures must use a trailing call.
- **Memoise parsed ASTs on the SourceFile, not on `id()`.** Object ids get
  recycled, which caused cross-run cache collisions. Store the tree as an
  attribute on the SourceFile instead.

## Environment / tooling

- **uv venv creation and sync can hang under a sandbox** that blocks the
  interpreter symlink pointing outside the working directory. Run uv commands
  (venv, sync, run, pytest) with the sandbox disabled.
- **`dev-mode-dirs` in pyproject can emit a `.pth` without a trailing newline**,
  which Python's `site` module silently refuses to process. Prefer
  `[tool.pytest.ini_options] pythonpath = ["src"]` for test imports.
- **Racing `uv run` invocations during a build can corrupt the venv.** If imports
  start failing in odd ways (e.g. a dependency's submodule goes missing), recreate
  the environment cleanly rather than debugging the corruption.
- **Ship non-`.py` assets via hatchling `force-include`** and make
  `loop_template/` and `data/` real packages (with `__init__.py`) so
  `importlib.resources.files(...)` can find them in the installed wheel.

## YAML gotchas

- A list item that *starts* with a special character — `"`, `` ` ``, `#` — is
  parsed as something other than a plain scalar and usually errors. Rewrite the
  prose so items begin with an ordinary word, or quote the entire value.

## The loop

- **`campaign.json` is the single source of truth** and append-only. The recorder
  in `check_invariants.py` is the only writer during a run.
- **Revert regressions; never record them.** The harness re-judges after each
  edit and `git reset --hard` if the Score dropped or violations rose, so the
  ledger only ever contains genuine improvements.
- **Keep the Python driver thin.** Worktree setup, baseline capture, and audit
  validation live in Python; the iteration loop and engine invocation live in
  `ralph.sh`. This keeps each piece independently testable.
