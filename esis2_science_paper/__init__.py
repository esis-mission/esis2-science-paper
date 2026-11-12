"""
Create the figures and compile the LaTeX files for this article.
"""

from . import figures, sections, tables
from ._acronyms import acronyms
from ._authors import authors
from ._document import document, pdf
from ._export import export
from ._keywords import keywords
from ._preamble import preamble
from ._spectrum import lines
from ._synthetic import image_synthetic, scene_synthetic, snr_synthetic
from ._variables import variables

directory_generated = "generated"
"""
The directory, inside the manuscript, of the files :func:`export` writes on
every delivery: the image of each figure and the macro of each number.

Everything in it is replaced when the article is next delivered, so it is
the one part of the manuscript which is not edited by hand.
"""

directory_sections = "sections"
"""The directory, inside the manuscript, of the file of each section."""

filename_main = "esis2-science.tex"
"""
The main file of the manuscript.

:func:`export` seeds the manuscript only if it does not have this file yet,
so that a delivery never overwrites the prose.
"""

filename_variables = "variables.tex"
r"""
The file, inside :data:`directory_generated`, which defines a macro for
every number cited in the prose, such as ``\cadence``.
"""

filename_acronyms = "acronyms.tex"
r"""
The file, beside the main file of the manuscript, which defines the acronyms
of the article, such as ``\CTIS``.

It is seeded once, like the prose, so the authors can add and change
acronyms in the manuscript.
"""

names_sections = (
    "00_abstract",
    "01_introduction",
    "02_motivation",
    "03_instrument",
    "04_inversions",
    "05_conclusions",
)
"""
The name of the file, inside :data:`directory_sections`, each section of the
article is seeded into, in the order the sections appear.

Each is numbered, so that the files are listed in the order they are read.
"""

__all__ = [
    "acronyms",
    "authors",
    "directory_generated",
    "directory_sections",
    "document",
    "export",
    "figures",
    "filename_acronyms",
    "filename_main",
    "filename_variables",
    "image_synthetic",
    "keywords",
    "lines",
    "names_sections",
    "pdf",
    "preamble",
    "scene_synthetic",
    "sections",
    "snr_synthetic",
    "tables",
    "variables",
]
