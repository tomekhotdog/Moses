"""Configuration: Weight table, MVP enabled-set, and the Config dataclass."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path

import yaml

# Integer Weights summing to 100 across all 31 Commandments.
# Calibrated via the offline optimizer (see evals/calibrate.py); renormalized
# from tuned floats to integers summing to 100 (largest-remainder rounding).
WEIGHTS: dict[int, int] = {
    1: 2,
    2: 4,
    3: 2,
    4: 3,
    5: 5,
    6: 3,
    7: 2,
    8: 3,
    9: 3,
    10: 2,
    11: 3,
    12: 16,
    13: 3,
    14: 1,
    15: 1,
    16: 5,
    17: 1,
    18: 2,
    19: 3,
    20: 4,
    21: 2,
    22: 3,
    23: 2,
    24: 4,
    25: 3,
    26: 3,
    27: 1,
    28: 3,
    29: 2,
    30: 7,
    31: 2,
}

assert sum(WEIGHTS.values()) == 100, f"Weights must sum to 100, got {sum(WEIGHTS.values())}"

# Global score-sharpening exponent applied to each rule score before the
# weighted mean (calibrated alongside WEIGHTS by the offline optimizer).
DEFAULT_GAMMA: float = 0.75


def _default_rule_configs() -> dict:
    # Lazy import: commandments import config, so importing at module level
    # would create a cycle.
    from .commandments import default_rule_configs

    return default_rule_configs()


# The MVP enabled-set. Mutation (#20) is in the set but only runs under --deep.
# C30 (pattern parsimony) was promoted after corpus validation showed it cleanly
# flags class-based over-engineering with no false positives. C4/C8 stay out.
MVP_COMMANDMENTS: set[int] = {
    1, 2, 3, 5, 6, 11, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 27, 29, 30, 31,
}


def _to_jsonable(value):
    if isinstance(value, (set, frozenset)):
        return sorted(value)
    return value


@dataclass(frozen=True)
class CommandmentsConfig:
    """Master scoring config: every rule's RuleConfig plus the Weights."""

    configs: dict  # number -> that rule's RuleConfig
    weights: dict  # number -> relative importance (int)
    gamma: float = DEFAULT_GAMMA  # global score-sharpening exponent

    @classmethod
    def default(cls) -> "CommandmentsConfig":
        return cls(configs=_default_rule_configs(), weights=dict(WEIGHTS), gamma=DEFAULT_GAMMA)

    def config_for(self, number: int):
        return self.configs.get(number)

    def weight_for(self, number: int) -> int:
        return self.weights.get(number, 0)

    def with_config(self, number: int, rule_config) -> "CommandmentsConfig":
        configs = dict(self.configs)
        configs[number] = rule_config
        return CommandmentsConfig(configs=configs, weights=dict(self.weights), gamma=self.gamma)

    def with_weight(self, number: int, weight: int) -> "CommandmentsConfig":
        weights = dict(self.weights)
        weights[number] = weight
        return CommandmentsConfig(configs=dict(self.configs), weights=weights, gamma=self.gamma)

    def with_gamma(self, gamma: float) -> "CommandmentsConfig":
        return CommandmentsConfig(
            configs=dict(self.configs), weights=dict(self.weights), gamma=gamma
        )

    def to_dict(self) -> dict:
        return {
            "weights": dict(self.weights),
            "gamma": self.gamma,
            "configs": {
                n: {k: _to_jsonable(v) for k, v in asdict(rc).items()}
                for n, rc in self.configs.items()
            },
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CommandmentsConfig":
        defaults = _default_rule_configs()
        configs = {}
        for n, fields in data.get("configs", {}).items():
            n = int(n)
            if n not in defaults:
                continue  # unknown/stale rule number from another version
            default_rc = defaults[n]
            coerced = {}
            for k, v in fields.items():
                cur = getattr(default_rc, k, None)
                if isinstance(cur, frozenset):
                    coerced[k] = frozenset(v)
                elif isinstance(cur, set):
                    coerced[k] = set(v)
                else:
                    coerced[k] = v
            configs[n] = type(default_rc)(**coerced)
        for n, rc in defaults.items():
            configs.setdefault(n, rc)
        weights = {int(k): int(v) for k, v in data.get("weights", WEIGHTS).items()}
        if not weights:
            weights = dict(WEIGHTS)
        gamma = float(data.get("gamma", DEFAULT_GAMMA))
        return cls(configs=configs, weights=weights, gamma=gamma)


@dataclass
class Config:
    """Runtime configuration for a Moses run."""

    enabled: set[int] = field(default_factory=lambda: set(MVP_COMMANDMENTS))
    excludes: list[str] = field(default_factory=list)
    deep: bool = False  # enables opt-in #20 mutation
    jscpd_path: str | None = None  # external duplication tool for #16
    mutmut_path: str | None = None  # override binary for #20
    # Master scoring config: per-rule RuleConfig + weights (calibration surface)
    commandments: CommandmentsConfig = field(default_factory=CommandmentsConfig.default)

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
            commandments=self.commandments,
        )
