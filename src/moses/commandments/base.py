"""Base helpers shared across Commandment implementations."""

from __future__ import annotations

from ..config import WEIGHTS
from ..models import CommandmentResult


class Commandment:
    """Base class. Subclasses set ``number`` and ``name`` and override ``evaluate``."""

    number: int = 0
    name: str = ""

    @property
    def weight(self) -> int:
        return WEIGHTS[self.number]

    def evaluate(self, codebase) -> CommandmentResult:  # pragma: no cover - abstract
        raise NotImplementedError


def not_measured(number: int, name: str) -> CommandmentResult:
    """A result for a Commandment that is not implemented / not applicable.

    Defaults to ScoreContribution 100 with status ``not_measured`` so that
    disabling/skipping never pads the Score (the engine excludes these from the
    weighted mean).
    """
    return CommandmentResult(
        number=number,
        name=name,
        weight=WEIGHTS[number],
        metric=None,
        score_contribution=100.0,
        status="not_measured",
        detail={},
        violations=[],
    )
