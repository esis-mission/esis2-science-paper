"""
The figures of this article, each a factory function returning an
:class:`aastex.Figure` which holds its image.

The ``figure`` environment of each, with its caption, is in the manuscript.
"""

import aastex

from ._bunch import bunch, lines_detected, num_emission_lines
from ._contribution import contribution
from ._field_stop_projections import field_stop_projections
from ._synthetic_image import synthetic_image

__all__ = [
    "bunch",
    "contribution",
    "field_stop_projections",
    "figures",
    "lines_detected",
    "num_emission_lines",
    "synthetic_image",
]


def figures() -> list[aastex.Figure]:
    """
    Every figure of the article, in the order they appear.

    A new figure is added here, so that its image is delivered to the
    manuscript.
    """
    return [
        bunch(),
        contribution(),
        field_stop_projections(),
        synthetic_image(),
    ]
