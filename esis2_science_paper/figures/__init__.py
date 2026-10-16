"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure`.
"""

from ._bunch import bunch, num_emission_lines
from ._contribution import contribution
from ._field_stop_projections import field_stop_projections
from ._synthetic_image import synthetic_image

__all__ = [
    "bunch",
    "contribution",
    "field_stop_projections",
    "num_emission_lines",
    "synthetic_image",
]
