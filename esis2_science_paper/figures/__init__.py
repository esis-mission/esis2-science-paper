"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._bunch import bunch, num_emission_lines
from ._contribution import contribution

__all__ = [
    "bunch",
    "contribution",
    "num_emission_lines",
]
