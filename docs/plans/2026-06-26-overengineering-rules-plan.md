# C30 + C4 — Over-engineering Rules Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use tomek-superpowers:build to implement this plan task-by-task.

**Goal:** Implement C30 (pattern parsimony / over-engineering) and C4 (layers add abstraction / delegation wrappers) as deterministic rules, registered but kept OUT of MVP, then validate they fire on the corpus's over-engineered solutions.
**Architecture:** Two new `commandments/cNN_*.py` modules each with a frozen `RuleConfig` + `evaluate(self, codebase, config)`, registered in `ALL_COMMANDMENTS` (the `default_rule_configs()` registry + `CommandmentsConfig` pick them up automatically). C30 = over-engineered-class ratio; C4 = delegation-wrapper-class ratio.
**Tech Stack:** Python stdlib `ast`, `_ast_helpers`, pytest.
**Design:** `docs/plans/2026-06-26-overengineering-rules-design.md`

Work on `main`. Tests: `uv run pytest`. Behaviour gate: both rules are OUT of MVP, so default `Config()` runs don't invoke them → full suite green AND `evals/corpus/moses_scores.json` (default-MVP scoring) unchanged after Tasks 1–2.

---

### Task 1: C30 — Pattern parsimony
**Depends on:** none

**Files:**
- Create: `src/moses/commandments/c30_pattern_parsimony.py`
- Modify: `src/moses/commandments/__init__.py`
- Test: `tests/unit/test_c30_pattern_parsimony.py`

**Step 1: Write the failing test** — create `tests/unit/test_c30_pattern_parsimony.py`:
```python
"""C30 pattern parsimony: penalise over-engineering (lone abstractions, tiny classes)."""

from __future__ import annotations

from pathlib import Path

from moses.commandments.c30_pattern_parsimony import PatternParsimony, RuleConfig
from moses.models import Codebase, SourceFile


def _cb(text: str) -> Codebase:
    return Codebase(root=Path("."), files=[SourceFile(path=Path("m.py"), relpath="m.py", text=text)])


OVER_ENGINEERED = '''
from abc import ABC, abstractmethod

class Strategy(ABC):
    @abstractmethod
    def run(self): ...

class OneStrat(Strategy):
    def run(self): return 1

class Helper1:
    def go(self): return 1

class Helper2:
    def go(self): return 2
'''

GOOD = '''
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

class Grid:
    def __init__(self, cells):
        self.cells = cells
    def width(self): return len(self.cells[0])
    def height(self): return len(self.cells)
    def at(self, p): return self.cells[p.y][p.x]
'''

JUSTIFIED_ABSTRACTION = '''
from abc import ABC, abstractmethod

class Base(ABC):
    @abstractmethod
    def a(self): ...
    @abstractmethod
    def b(self): ...

class ImplOne(Base):
    def a(self): return 1
    def b(self): return 2
    def c(self): return 3

class ImplTwo(Base):
    def a(self): return 4
    def b(self): return 5
    def d(self): return 6
'''


def test_over_engineered_scores_low():
    r = PatternParsimony().evaluate(_cb(OVER_ENGINEERED), RuleConfig())
    assert r.status == "measured"
    assert r.score_contribution < 30
    assert any(v["reason"] == "lone_abstraction" for v in r.violations)
    assert any(v["reason"] == "tiny_class" for v in r.violations)


def test_good_code_not_penalised():
    r = PatternParsimony().evaluate(_cb(GOOD), RuleConfig())
    # Point is an excluded dataclass; Grid has 3 real methods -> not flagged.
    assert r.status == "measured"
    assert r.violations == []
    assert r.score_contribution == 100.0


def test_functional_code_not_measured():
    r = PatternParsimony().evaluate(_cb("def f(x: int) -> int:\n    return x + 1\n"), RuleConfig())
    assert r.status == "not_measured"


def test_abstraction_with_two_impls_not_lone():
    r = PatternParsimony().evaluate(_cb(JUSTIFIED_ABSTRACTION), RuleConfig())
    # Base has 2 in-codebase subclasses -> not a lone abstraction; 2 methods -> not tiny.
    assert all(v["function"] != "Base" for v in r.violations)
```

**Step 2: Run to verify it fails**
Run: `uv run pytest tests/unit/test_c30_pattern_parsimony.py -q` → FAIL (no module).

**Step 3: Implement** — create `src/moses/commandments/c30_pattern_parsimony.py`:
```python
"""Commandment 30 — Pattern parsimony.

Over-engineering detector: the fraction of (eligible) classes that are needless
abstraction machinery — a *lone* abstraction (ABC / @abstractmethod with <=1
in-codebase subclass) or a *tiny* class (<= tiny_method_max non-dunder methods).
Data-ish types (dataclass / Enum / NamedTuple / Exception / Protocol) are excluded
so this never fights C27 (which rewards small data types). Curve: 100 - slope*ratio.
"""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_dunder, iter_classes, methods_of

NUMBER = 30
NAME = "Pattern parsimony"

_DATA_BASES = frozenset({"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag", "NamedTuple"})
_EXCEPTION_BASES = frozenset({"Exception", "BaseException"})


@dataclass(frozen=True)
class RuleConfig:
    slope: float = 150.0
    tiny_method_max: int = 1


def _base_names(cls: ast.ClassDef) -> list[str]:
    names = []
    for base in cls.bases:
        if isinstance(base, ast.Name):
            names.append(base.id)
        elif isinstance(base, ast.Attribute):
            names.append(base.attr)
    return names


def _decorator_names(node) -> list[str]:
    names = []
    for dec in node.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if isinstance(target, ast.Name):
            names.append(target.id)
        elif isinstance(target, ast.Attribute):
            names.append(target.attr)
    return names


def _is_excluded(cls: ast.ClassDef) -> bool:
    """Data-ish types that legitimately have few methods — not over-engineering."""
    if "dataclass" in _decorator_names(cls):
        return True
    bases = set(_base_names(cls))
    if bases & _DATA_BASES or bases & _EXCEPTION_BASES:
        return True
    if any(b.endswith("Error") or b.endswith("Exception") for b in bases):
        return True
    if "Protocol" in bases:  # structural typing, not nominal over-abstraction
        return True
    return False


def _metaclass_is_abcmeta(cls: ast.ClassDef) -> bool:
    for kw in cls.keywords:
        if kw.arg == "metaclass":
            v = kw.value
            name = v.id if isinstance(v, ast.Name) else getattr(v, "attr", "")
            if name == "ABCMeta":
                return True
    return False


def _is_abstraction(cls: ast.ClassDef) -> bool:
    if "ABC" in set(_base_names(cls)) or _metaclass_is_abcmeta(cls):
        return True
    return any("abstractmethod" in _decorator_names(m) for m in methods_of(cls))


def _non_dunder_method_count(cls: ast.ClassDef) -> int:
    return sum(1 for m in methods_of(cls) if not is_dunder(m.name))


class PatternParsimony:
    number = NUMBER
    name = NAME
    RuleConfig = RuleConfig

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult:
        classes = list(iter_classes(codebase))
        names_present = {cls.name for _, cls in classes}
        subclass_count: Counter = Counter()
        for _, cls in classes:
            for b in _base_names(cls):
                if b in names_present:
                    subclass_count[b] += 1

        eligible = 0
        violations = []
        for source, cls in classes:
            if _is_excluded(cls):
                continue
            eligible += 1
            tiny = _non_dunder_method_count(cls) <= config.tiny_method_max
            lone = _is_abstraction(cls) and subclass_count[cls.name] <= 1
            if tiny or lone:
                violations.append(
                    {
                        "file": source.relpath,
                        "line": cls.lineno,
                        "function": cls.name,
                        "reason": "lone_abstraction" if lone else "tiny_class",
                    }
                )

        if eligible == 0:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = len(violations) / eligible
        score = clamp(100 - config.slope * m)
        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 3),
            score_contribution=score,
            status="measured",
            detail={"over_engineered": len(violations), "eligible_classes": eligible},
            violations=violations[:50],
        )
```
Register in `src/moses/commandments/__init__.py`: add `from .c30_pattern_parsimony import PatternParsimony` with the other imports, and add `PatternParsimony(),` to `ALL_COMMANDMENTS` (place near the end / numeric order, after `Composition()`). Read the file first to match formatting.

**Step 4: Run tests + behaviour gate**
- `uv run pytest tests/unit/test_c30_pattern_parsimony.py -q` → PASS.
- `uv run pytest -q` → full suite green (1 pre-existing skip OK).
- Behaviour gate: `uv run python evals/corpus_score.py --corpus evals/corpus` then `git diff --stat evals/corpus/moses_scores.json` → EMPTY (C30 not in MVP, default scoring unchanged). Do not commit moses_scores.json.

**Step 5: Commit**
```bash
git add src/moses/commandments/c30_pattern_parsimony.py src/moses/commandments/__init__.py tests/unit/test_c30_pattern_parsimony.py
git commit -m "feat(c30): pattern parsimony — over-engineering detector (out of MVP)"
```

---

### Task 2: C4 — Layers add abstraction (delegation wrappers)
**Depends on:** Task 1 (both touch __init__.py; run sequentially)

**Files:**
- Create: `src/moses/commandments/c04_layers.py`
- Modify: `src/moses/commandments/__init__.py`
- Test: `tests/unit/test_c04_layers.py`

**Step 1: Write the failing test** — create `tests/unit/test_c04_layers.py`:
```python
"""C4 layers add abstraction: penalise delegation-wrapper classes."""

from __future__ import annotations

from pathlib import Path

from moses.commandments.c04_layers import Layers, RuleConfig
from moses.models import Codebase, SourceFile


def _cb(text: str) -> Codebase:
    return Codebase(root=Path("."), files=[SourceFile(path=Path("m.py"), relpath="m.py", text=text)])


WRAPPER = '''
class Store:
    def __init__(self, backend):
        self.backend = backend
    def read(self, k): return self.backend.read(k)
    def write(self, k, v): return self.backend.write(k, v)
    def delete(self, k): return self.backend.delete(k)
'''

ADAPTER = '''
class Adapter:
    def __init__(self, backend):
        self.backend = backend
    def get(self, k): return self.backend.fetch(k)
    def put(self, k, v): return self.backend.store(k, v)
    def remove(self, k): return self.backend.erase(k)
'''

REAL = '''
class Grid:
    def __init__(self, cells):
        self.cells = cells
    def width(self): return len(self.cells[0])
    def neighbours(self, p): return [p]
    def at(self, p): return self.cells[p]
'''


def test_delegation_wrapper_scores_low():
    r = Layers().evaluate(_cb(WRAPPER), RuleConfig())
    assert r.status == "measured"
    assert r.score_contribution < 30
    assert any(v["function"] == "Store" for v in r.violations)


def test_adapter_that_transforms_not_flagged():
    # forwards under DIFFERENT names -> genuine adaptation, not a pass-through layer.
    r = Layers().evaluate(_cb(ADAPTER), RuleConfig())
    assert r.violations == []
    assert r.score_contribution == 100.0


def test_real_class_not_flagged():
    r = Layers().evaluate(_cb(REAL), RuleConfig())
    assert r.violations == []
    assert r.score_contribution == 100.0


def test_no_classes_not_measured():
    r = Layers().evaluate(_cb("def f(x):\n    return x\n"), RuleConfig())
    assert r.status == "not_measured"
```

**Step 2: Run to verify it fails**
Run: `uv run pytest tests/unit/test_c04_layers.py -q` → FAIL (no module).

**Step 3: Implement** — create `src/moses/commandments/c04_layers.py`:
```python
"""Commandment 4 — Layers add abstraction.

Detects delegation-wrapper classes: a class that stores an injected object and
forwards >= min_forwarders public methods to it BY THE SAME NAME (>= forward_fraction
of its public methods) — a layer that adds no abstraction over the wrapped object.
Same-name requirement spares genuine Adapters/Facades that transform the interface.
Metric: wrapper classes / total classes. Curve: 100 - slope*ratio.
"""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass

from ..models import CommandmentResult
from ._ast_helpers import clamp, is_dunder, is_private, iter_classes, methods_of

NUMBER = 4
NAME = "Layers add abstraction"


@dataclass(frozen=True)
class RuleConfig:
    slope: float = 200.0
    min_forwarders: int = 3
    forward_fraction: float = 0.6


def _self_name(method) -> str | None:
    args = method.args.args
    return args[0].arg if args else None


def _wrapped_attrs(cls: ast.ClassDef) -> set[str]:
    """self.<attr> names assigned directly from an __init__ parameter."""
    attrs: set[str] = set()
    for m in methods_of(cls):
        if m.name != "__init__":
            continue
        params = {a.arg for a in m.args.args}
        self_name = _self_name(m)
        for node in ast.walk(m):
            if isinstance(node, ast.Assign) and len(node.targets) == 1:
                tgt = node.targets[0]
                if (
                    isinstance(tgt, ast.Attribute)
                    and isinstance(tgt.value, ast.Name)
                    and tgt.value.id == self_name
                    and isinstance(node.value, ast.Name)
                    and node.value.id in params
                ):
                    attrs.add(tgt.attr)
    return attrs


def _forwards_to(method, self_name: str | None) -> str | None:
    """If body is a single `self.<attr>.<same name>(...)`, return <attr>, else None."""
    body = [
        s
        for s in method.body
        if not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))
    ]
    if len(body) != 1:
        return None
    stmt = body[0]
    call = stmt.value if isinstance(stmt, (ast.Return, ast.Expr)) else None
    if not isinstance(call, ast.Call) or not isinstance(call.func, ast.Attribute):
        return None
    if call.func.attr != method.name:  # same-name forwarding only
        return None
    inner = call.func.value
    if isinstance(inner, ast.Attribute) and isinstance(inner.value, ast.Name) and inner.value.id == self_name:
        return inner.attr
    return None


def _is_delegation_wrapper(cls: ast.ClassDef, config: RuleConfig) -> bool:
    wrapped = _wrapped_attrs(cls)
    if not wrapped:
        return False
    public = [m for m in methods_of(cls) if not is_dunder(m.name) and not is_private(m.name)]
    if not public:
        return False
    fwd: Counter = Counter()
    for m in public:
        attr = _forwards_to(m, _self_name(m))
        if attr in wrapped:
            fwd[attr] += 1
    if not fwd:
        return False
    best = max(fwd.values())
    return best >= config.min_forwarders and best / len(public) >= config.forward_fraction


class Layers:
    number = NUMBER
    name = NAME
    RuleConfig = RuleConfig

    @property
    def weight(self) -> int:
        from ..config import WEIGHTS

        return WEIGHTS[NUMBER]

    def evaluate(self, codebase, config: RuleConfig) -> CommandmentResult:
        total = 0
        violations = []
        for source, cls in iter_classes(codebase):
            total += 1
            if _is_delegation_wrapper(cls, config):
                violations.append(
                    {"file": source.relpath, "line": cls.lineno, "function": cls.name}
                )

        if total == 0:
            return CommandmentResult(NUMBER, NAME, self.weight, status="not_measured")

        m = len(violations) / total
        score = clamp(100 - config.slope * m)
        return CommandmentResult(
            number=NUMBER,
            name=NAME,
            weight=self.weight,
            metric=round(m, 3),
            score_contribution=score,
            status="measured",
            detail={"wrappers": len(violations), "class_count": total},
            violations=violations[:50],
        )
```
Register in `__init__.py`: add `from .c04_layers import Layers` and `Layers(),` in `ALL_COMMANDMENTS` (near the start / numeric order, e.g. after `PassThrough()`).

**Step 4: Run tests + behaviour gate**
- `uv run pytest tests/unit/test_c04_layers.py -q` → PASS.
- `uv run pytest -q` → full suite green.
- Behaviour gate: re-score, `git diff --stat evals/corpus/moses_scores.json` → EMPTY (C4 not in MVP).

**Step 5: Commit**
```bash
git add src/moses/commandments/c04_layers.py src/moses/commandments/__init__.py tests/unit/test_c04_layers.py
git commit -m "feat(c4): layers add abstraction — delegation-wrapper detector (out of MVP)"
```

---

### Task 3: Validate on the corpus (MVP-promotion gate)
**Depends on:** Tasks 1, 2

This is analysis, not new product code. Confirm C4+C30 actually fire on the corpus's known over-engineered solutions before anyone promotes them to MVP.

**Steps:**
1. Score the corpus with C4+C30 ENABLED (in addition to MVP) and inspect their per-solution results:
```bash
uv run python -c "
import json
from pathlib import Path
from moses.config import Config, MVP_COMMANDMENTS
from moses.engine import run
cfg = Config(enabled=set(MVP_COMMANDMENTS) | {4, 30})
targets = ['2024_q10/online_1.py','2024_q21/online_1.py','2022_q11/online_1.py','2024_q10/tomek.py']
for t in targets:
    q, sol = t.split('/')
    v = run(Path('evals/corpus')/q/sol, cfg)
    c4 = next(c for c in v.commandments if c.number==4)
    c30 = next(c for c in v.commandments if c.number==30)
    print(f'{t:28} C4={c4.status}:{c4.score_contribution}  C30={c30.status}:{c30.score_contribution}')
"
```
2. Also spot-check that a clean solution (e.g. `2024_q10/synth_clean.py`) is NOT heavily penalised by C4/C30 (no false positives).
3. Write findings to a short section appended to the design doc (`docs/plans/2026-06-26-overengineering-rules-design.md`) under "## Validation results": which over-engineered solutions C30/C4 flagged, any false positives on clean code, and a recommendation on whether to promote to MVP (and at what slope). Do NOT add to MVP in this task — that's a separate, deliberate calibration step.

**Commit:**
```bash
git add docs/plans/2026-06-26-overengineering-rules-design.md
git commit -m "docs(c30,c4): corpus validation results + MVP-promotion recommendation"
```

---

## Review
- [ ] Code review requested (C30 + C4 metric correctness; overlap-with-C3/C27 sanity)
- [ ] All feedback addressed
- [ ] Final verification (`uv run pytest` green; default `moses_scores.json` unchanged; validation shows C30/C4 fire on over-engineered solutions without flagging clean ones)
