"""
Create the figures and compile the LaTeX files for this article.
"""

from . import figures, sections, tables
from ._acronyms import acronyms
from ._authors import authors
from ._document import document, pdf
from ._keywords import keywords
from ._preamble import preamble
from ._spectrum import lines
from ._synthetic import image_synthetic, scene_synthetic, snr_synthetic
from ._variables import variables

__all__ = [
    "acronyms",
    "authors",
    "document",
    "figures",
    "image_synthetic",
    "keywords",
    "lines",
    "pdf",
    "preamble",
    "scene_synthetic",
    "sections",
    "snr_synthetic",
    "tables",
    "variables",
]
