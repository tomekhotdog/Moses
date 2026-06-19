"""Static metadata for all 31 Commandments: names, weights, source links.

Used by reports and to construct ``not_measured`` placeholders for rules that
have no implementation yet.
"""

from __future__ import annotations

from ..config import WEIGHTS

# number -> (name, source attribution)
DESCRIPTIONS: dict[int, tuple[str, str]] = {
    1: ("Deep modules", "Ousterhout, APoSD ch.4"),
    2: ("Loose coupling", "Ousterhout; GoF"),
    3: ("No pass-through methods", "Ousterhout, APoSD ch.7"),
    4: ("Layers add abstraction", "Ousterhout, APoSD ch.7"),
    5: ("Pull complexity downward", "Ousterhout, APoSD ch.8"),
    6: ("Define errors out of existence", "Ousterhout, APoSD ch.10"),
    7: ("Comment where complexity demands it", "Ousterhout; McConnell"),
    8: ("Strategic over tactical", "Ousterhout, APoSD ch.3"),
    9: ("Meaningful names", "Martin, Clean Code ch.2"),
    10: ("One name per concept", "Martin, Clean Code ch.2"),
    11: ("Small functions", "Martin, Clean Code ch.3"),
    12: ("Low cognitive complexity", "SonarSource; McConnell"),
    13: ("Few parameters", "Martin, Clean Code ch.3"),
    14: ("Shallow nesting", "McConnell, Code Complete ch.19"),
    15: ("Command-query separation", "Meyer; Martin"),
    16: ("DRY", "Hunt & Thomas; Martin"),
    17: ("No commented-out code", "Martin, Clean Code ch.4"),
    18: ("No empty catch blocks", "McConnell; Martin"),
    19: ("Test isolation", "Martin, Clean Code ch.9"),
    20: ("Mutation kill rate", "Mutation testing literature"),
    21: ("Cohesive classes", "Martin (LCOM); GoF"),
    22: ("Law of Demeter", "Lieberherr; Martin"),
    23: ("Narrow variable scope", "McConnell, Code Complete ch.10"),
    24: ("Prefer immutability", "Effective Java; FP practice"),
    25: ("No magic numbers", "Martin; McConnell"),
    26: ("Validate at boundaries", "Ousterhout; defensive programming"),
    27: ("Data over primitives", "Fowler, primitive obsession"),
    28: ("Program to interfaces", "GoF; DIP"),
    29: ("Composition over inheritance", "GoF, Design Patterns"),
    30: ("Pattern parsimony", "GoF; Ousterhout"),
    31: ("Contain class complexity", "Martin (WMC); McConnell"),
}


def name_for(number: int) -> str:
    return DESCRIPTIONS[number][0]


def source_for(number: int) -> str:
    return DESCRIPTIONS[number][1]


def weight_for(number: int) -> int:
    return WEIGHTS[number]


ALL_NUMBERS: list[int] = sorted(DESCRIPTIONS.keys())
