import pathlib
import shutil
import subprocess

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

    The article is compiled from the files :func:`export` seeds a new
    manuscript with, in a directory of its own, so that what is built here
    is what the authors are given in Overleaf.

    ``latexmk`` is required, since it runs BibTeX and repeats the build
    until the citations and the cross-references are resolved.
    """

    if shutil.which("latexmk") is None:
        raise FileNotFoundError(
            "`latexmk` is needed to build the article, and was not found"
        )

    # Built from nothing every time, since a manuscript with a main file
    # already would keep its old prose.
    directory = pathlib.Path(__file__).parent / "build"
    shutil.rmtree(directory, ignore_errors=True)

    esis2_science_paper.export(directory)

    main = esis2_science_paper.filename_main
    result = subprocess.run(
        [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-halt-on-error",
            main,
        ],
        cwd=directory,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"latexmk failed to build {main} in {directory}:\n"
            f"{result.stdout[-3000:]}"
        )

    return (directory / main).with_suffix(".pdf")
