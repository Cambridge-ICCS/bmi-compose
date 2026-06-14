"""bmi_compose - Compositional combinators for BMI models."""

from .compose import compose, union, intersection, composeConfig, splitConf, CouplingType
from .identity import IdentityBmi
from .pymt_compose import composed_setup

__all__ = [
    "compose",
    "union",
    "intersection",
    "composeConfig",
    "splitConf",
    "CouplingType",
    "IdentityBmi",
    "composed_setup",
]
