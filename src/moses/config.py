"""Configuration: Weight table, MVP enabled-set, and the Config dataclass."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

# Integer Weights summing to 100 across all 31 Commandments.
WEIGHTS: dict[int, int] = {
    1: 8,
    2: 5,
    3: 2,
    4: 3,
    5: 3,
    6: 3,
    7: 2,
    8: 4,
    9: 4,
    10: 2,
    11: 2,
    12: 6,
    13: 4,
    14: 2,
    15: 2,
    16: 6,
    17: 1,
    18: 2,
    19: 3,
    20: 5,
    21: 2,
    22: 3,
    23: 2,
    24: 3,
    25: 2,
    26: 3,
    27: 3,
    28: 4,
    29: 3,
    30: 3,
    31: 3,
}

assert sum(WEIGHTS.values()) == 100, f"Weights must sum to 100, got {sum(WEIGHTS.values())}"


def _default_rule_params() -> dict:
    # Lazy import: commandments import config, so importing at module level
    # would create a cycle.
    from .commandments import default_rule_params

    return default_rule_params()


# The MVP enabled-set. Mutation (#20) is in the set but only runs under --deep.
MVP_COMMANDMENTS: set[int] = {
    1, 2, 3, 5, 6, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 29, 31,
}


@dataclass
class Config:
    """Runtime configuration for a Moses run."""

    enabled: set[int] = field(default_factory=lambda: set(MVP_COMMANDMENTS))
    excludes: list[str] = field(default_factory=list)
    deep: bool = False  # enables opt-in #20 mutation
    jscpd_path: str | None = None  # external duplication tool for #16
    mutmut_path: str | None = None  # override binary for #20
    # number -> that rule's frozen Params (calibration override surface)
    rule_params: dict[int, object] = field(default_factory=_default_rule_params)

    def is_enabled(self, number: int) -> bool:
        if number not in self.enabled:
            return False
        if number == 20 and not self.deep:
            return False
        return True

    @classmethod
    def from_file(cls, path: str | Path) -> "Config":
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
        cfg = cls()
        if "enabled" in data:
            cfg.enabled = set(int(n) for n in data["enabled"])
        if "disabled" in data:
            cfg.enabled -= set(int(n) for n in data["disabled"])
        if "excludes" in data:
            cfg.excludes = list(data["excludes"])
        if "deep" in data:
            cfg.deep = bool(data["deep"])
        if "jscpd_path" in data:
            cfg.jscpd_path = data["jscpd_path"]
        if "mutmut_path" in data:
            cfg.mutmut_path = data["mutmut_path"]
        return cfg

    def with_overrides(
        self,
        enable: list[int] | None = None,
        disable: list[int] | None = None,
        exclude: list[str] | None = None,
        deep: bool | None = None,
    ) -> "Config":
        enabled = set(self.enabled)
        if enable:
            enabled |= set(enable)
        if disable:
            enabled -= set(disable)
        return Config(
            enabled=enabled,
            excludes=self.excludes + list(exclude or []),
            deep=self.deep if deep is None else deep,
            jscpd_path=self.jscpd_path,
            mutmut_path=self.mutmut_path,
            rule_params=self.rule_params,
        )
