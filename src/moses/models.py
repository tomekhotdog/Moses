"""Core domain models for Moses.

Canonical PascalCase terms: Commandment, Score, ScoreContribution, Grade,
Metric, Normalisation, Weight, Verdict, Hotspot, Codebase.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SourceFile:
    """A single Python source file loaded into the Codebase."""

    path: Path
    relpath: str
    text: str

    @property
    def loc(self) -> int:
        """Total physical lines."""
        return self.text.count("\n") + (1 if self.text and not self.text.endswith("\n") else 0)

    @property
    def non_blank_loc(self) -> int:
        return sum(1 for line in self.text.splitlines() if line.strip())

    @property
    def is_test(self) -> bool:
        name = self.path.name
        if name.startswith("test_") or name.endswith("_test.py"):
            return True
        parts = Path(self.relpath).parts
        return "tests" in parts or "test" in parts


@dataclass
class Codebase:
    """A loaded source tree."""

    root: Path
    files: list[SourceFile] = field(default_factory=list)

    @property
    def total_loc(self) -> int:
        return sum(f.loc for f in self.files)

    @property
    def non_blank_loc(self) -> int:
        return sum(f.non_blank_loc for f in self.files)

    def source_files(self, include_tests: bool = True) -> list[SourceFile]:
        if include_tests:
            return list(self.files)
        return [f for f in self.files if not f.is_test]


@dataclass
class CommandmentResult:
    """The outcome of evaluating one Commandment against a Codebase."""

    number: int
    name: str
    # The rule's default weight, kept for display/reporting only. The
    # authoritative scoring weight comes from CommandmentsConfig.weight_for.
    weight: int
    metric: float | None = None
    score_contribution: float = 100.0
    status: str = "not_measured"  # "measured" | "not_measured" | "error"
    detail: dict = field(default_factory=dict)
    violations: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "number": self.number,
            "name": self.name,
            "weight": self.weight,
            "metric": self.metric,
            "score_contribution": round(self.score_contribution, 2),
            "status": self.status,
            "detail": self.detail,
            "violations": self.violations,
        }


@dataclass
class Verdict:
    """The full result object for a single Moses run."""

    score: float
    grade: str
    commandments: list[CommandmentResult]
    hotspots: list[dict] = field(default_factory=list)
    overview: dict = field(default_factory=dict)
    meta: dict = field(default_factory=dict)
    schema_version: int = 1

    def to_dict(self) -> dict:
        return {
            "schema_version": self.schema_version,
            "score": round(self.score, 2),
            "grade": self.grade,
            "commandments": [c.to_dict() for c in self.commandments],
            "hotspots": self.hotspots,
            "overview": self.overview,
            "meta": self.meta,
        }


# Grade thresholds: A >= 80, B >= 65, C >= 50, D >= 35, E >= 20, F < 20
_GRADE_THRESHOLDS = [
    (80.0, "A"),
    (65.0, "B"),
    (50.0, "C"),
    (35.0, "D"),
    (20.0, "E"),
]


def grade_for(score: float) -> str:
    """Map a Score in [0, 100] to a Grade letter A-F."""
    for threshold, letter in _GRADE_THRESHOLDS:
        if score >= threshold:
            return letter
    return "F"
