"""Per-Commandment hint strings shown in reports and served by ``moses prompt N``.

The richer refactoring briefs live in ``data/commandment_prompts.yaml``; this
module loads them and falls back to a one-line hint built from descriptions.
"""

from __future__ import annotations

import functools
from importlib import resources

import yaml

from .commandments.descriptions import DESCRIPTIONS

# Short hints displayed in HTML/terminal reports.
HINTS: dict[int, str] = {
    1: "Deepen modules: more implementation behind a smaller interface.",
    2: "Reduce a class's references to imported names (CBO).",
    3: "Remove pass-through methods that just forward to another callable.",
    5: "Move required parameters into the callee; give sensible defaults.",
    6: "Design APIs so errors can't occur, rather than raising.",
    11: "Split functions so p95 LOC stays modest.",
    12: "Lower cognitive and cyclomatic complexity per function.",
    13: "Fewer parameters; bundle related ones into a value object.",
    14: "Flatten nesting via early returns and guard clauses.",
    15: "Separate commands (mutate) from queries (return).",
    16: "Eliminate duplicated token blocks (DRY).",
    17: "Delete commented-out code; rely on version control.",
    18: "Never swallow exceptions with an empty catch.",
    20: "Raise mutation kill rate with stronger assertions.",
    21: "Increase class cohesion (lower LCOM4).",
    22: "Honour the Law of Demeter; avoid long attribute chains.",
    23: "Narrow each local variable's live range.",
    24: "Prefer immutability; avoid reassigning locals.",
    25: "Replace magic numbers with named constants.",
    29: "Prefer composition over deep inheritance.",
    31: "Contain class complexity (lower WMC).",
}


@functools.lru_cache(maxsize=1)
def _load_yaml() -> dict:
    try:
        text = resources.files("moses.data").joinpath("commandment_prompts.yaml").read_text(
            encoding="utf-8"
        )
    except (FileNotFoundError, ModuleNotFoundError, OSError):
        return {}
    return yaml.safe_load(text) or {}


def hint_for(number: int) -> str:
    return HINTS.get(number, DESCRIPTIONS.get(number, ("", ""))[0])


def prompt_for(number: int) -> str:
    """Return the full curated refactoring brief for a Commandment."""
    data = _load_yaml()
    key = str(number)
    entry = data.get(key) or data.get(number)
    name = DESCRIPTIONS.get(number, ("Unknown", ""))[0]
    if not entry:
        return f"# Commandment {number}: {name}\n\n{hint_for(number)}\n"

    lines = [f"# Commandment {number}: {entry.get('name', name)}", ""]
    for section in ("summary", "target_shape", "violation_shape", "anti_patterns", "interactions"):
        if section in entry:
            lines.append(f"## {section.replace('_', ' ').title()}")
            value = entry[section]
            if isinstance(value, list):
                lines.extend(f"- {item}" for item in value)
            else:
                lines.append(str(value))
            lines.append("")
    return "\n".join(lines)
