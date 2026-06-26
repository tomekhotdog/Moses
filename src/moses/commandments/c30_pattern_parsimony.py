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
