"""Registry of implemented Commandment instances.

``ALL_COMMANDMENTS`` holds one instance per implemented rule. Rules not present
here are filled in by the engine as ``not_measured`` placeholders.
"""

from __future__ import annotations

from .c01_deep_modules import DeepModules
from .c02_loose_coupling import LooseCoupling
from .c03_pass_through import PassThrough
from .c04_layers import Layers
from .c05_pull_complexity_down import PullComplexityDown
from .c06_define_errors_out import DefineErrorsOut
from .c11_small_functions import SmallFunctions
from .c12_cognitive_complexity import LowCognitiveComplexity
from .c13_few_parameters import FewParameters
from .c14_shallow_nesting import ShallowNesting
from .c15_command_query import CommandQuery
from .c16_dry import DRY
from .c17_commented_out_code import NoCommentedOutCode
from .c18_empty_catch import NoEmptyCatch
from .c20_mutation import MutationKillRate
from .c21_cohesive_classes import CohesiveClasses
from .c22_law_of_demeter import LawOfDemeter
from .c23_narrow_scope import NarrowScope
from .c24_immutability import Immutability
from .c25_magic_numbers import NoMagicNumbers
from .c27_data_over_primitives import DataOverPrimitives
from .c29_composition import Composition
from .c30_pattern_parsimony import PatternParsimony
from .c31_class_complexity import ClassComplexity

ALL_COMMANDMENTS: list = [
    DeepModules(),
    LooseCoupling(),
    PassThrough(),
    Layers(),
    PullComplexityDown(),
    DefineErrorsOut(),
    SmallFunctions(),
    LowCognitiveComplexity(),
    FewParameters(),
    ShallowNesting(),
    CommandQuery(),
    DRY(),
    NoCommentedOutCode(),
    NoEmptyCatch(),
    MutationKillRate(),
    CohesiveClasses(),
    LawOfDemeter(),
    NarrowScope(),
    Immutability(),
    NoMagicNumbers(),
    DataOverPrimitives(),
    Composition(),
    PatternParsimony(),
    ClassComplexity(),
]


def default_rule_configs() -> dict:
    """Map each implemented rule number to a fresh default RuleConfig instance."""
    return {cmd.number: cmd.RuleConfig() for cmd in ALL_COMMANDMENTS}
