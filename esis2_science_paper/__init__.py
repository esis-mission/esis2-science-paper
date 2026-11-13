"""
Create the figures and the numbers of this article, and compile its manuscript.
"""

from . import figures
from ._export import export
from ._pdf import pdf
from ._spectrum import lines
from ._synthetic import image_synthetic, scene_synthetic, snr_synthetic
from ._variables import variables

directory_manuscript = "manuscript"
"""
The directory, at the root of the repository, of the prose of the article:
a copy of the Overleaf project in which the authors edit it.

Edits to it here are sent to Overleaf when they are merged, and edits made
in Overleaf are brought back by the ``overleaf`` workflow.
"""

directory_generated = "generated"
"""
The directory, inside the manuscript, of the files :func:`export` writes on
every delivery: the image of each figure and the macro of each number.

Everything in it is replaced when the article is next delivered, so it is
the one part of the manuscript which is not edited by hand, and it is not
kept in the repository.
"""

filename_main = "esis2-science.tex"
"""The main file of the manuscript."""

filename_variables = "variables.tex"
r"""
The file, inside :data:`directory_generated`, which defines a macro for
every number cited in the prose, such as ``\cadence``.
"""

__all__ = [
    "directory_generated",
    "directory_manuscript",
    "export",
    "figures",
    "filename_main",
    "filename_variables",
    "image_synthetic",
    "lines",
    "pdf",
    "scene_synthetic",
    "snr_synthetic",
    "variables",
]
