import pathlib

import aastex
import matplotlib.pyplot as plt

import esis2_science_paper

__all__ = [
    "document",
    "pdf",
]


def document() -> aastex.Document:
    """
    An :mod:`aastex` representation of the article.
    """

    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.size"] = 9
    plt.rcParams["lines.linewidth"] = 1

    doc = aastex.Document(
        document_options=[
            "twocolumn",
        ],
        lmodern=False,
        textcomp=False,
    )

    doc.packages.append(aastex.Package("amsmath"))
    doc.packages.append(aastex.Package("hyperref"))
    doc.packages.append(aastex.Package("siunitx"))

    doc.preamble += esis2_science_paper.preamble()
    doc.preamble += esis2_science_paper.acronyms()

    doc.variables += esis2_science_paper.variables()

    doc.append(
        aastex.Title(
            "Detecting Electron Beam Heating in Active Region Moss "
            "with the Second Flight of the EUV Snapshot Imaging Spectrograph"
        )
    )

    doc += esis2_science_paper.authors()

    doc.append(esis2_science_paper.sections.abstract())
    doc.append(esis2_science_paper.keywords())
    doc.append(esis2_science_paper.sections.introduction())
    doc.append(esis2_science_paper.sections.motivation())
    doc.append(esis2_science_paper.sections.instrument())
    doc.append(esis2_science_paper.sections.inversions())
    doc.append(esis2_science_paper.sections.conclusions())

    doc.append(aastex.Bibliography("sources"))

    return doc


def pdf() -> pathlib.Path:
    """
    Build a pdf version of :func:`document` and return the path of the document.
    """

    doc = document()

    path = pathlib.Path(__file__).parent / "esis2-science"
    doc.generate_pdf(
        filepath=path,
        clean_tex=False,
    )

    return path.with_suffix(".pdf")
