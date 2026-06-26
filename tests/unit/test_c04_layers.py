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
