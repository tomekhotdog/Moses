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
    assert r.status == "measured"
    assert r.violations == []
    assert r.score_contribution == 100.0


def test_functional_code_not_measured():
    r = PatternParsimony().evaluate(_cb("def f(x: int) -> int:\n    return x + 1\n"), RuleConfig())
    assert r.status == "not_measured"


def test_abstraction_with_two_impls_not_lone():
    r = PatternParsimony().evaluate(_cb(JUSTIFIED_ABSTRACTION), RuleConfig())
    assert all(v["function"] != "Base" for v in r.violations)
