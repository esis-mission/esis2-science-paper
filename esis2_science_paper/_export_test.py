import collections.abc
import pathlib

import aastex
import astropy.units as u
import matplotlib.pyplot as plt
import pytest

import esis2_science_paper
from esis2_science_paper._export import _export

_names = ("00_abstract", "01_introduction")
"""The names of the files of the sections of :func:`_document`."""


def _document(labels: tuple[str, ...] = ("fig:test",)) -> aastex.Document:
    """
    A small article in the form of this one: two acronyms, an abstract, and a
    section holding a figure for each label whose caption cites a number.
    """
    result = aastex.Document()
    result.preamble.append(aastex.Acronym("CTIS", "computed tomography", plural=True))
    result.preamble.append(aastex.Acronym("EUV", "extreme ultraviolet"))
    result.variables.append(aastex.Variable(name="cadence", value=2 * u.s))
    result.append(aastex.Title("A Test"))

    abstract = aastex.Abstract()
    abstract.append(r"An abstract citing \cadence.")
    result.append(abstract)

    section = aastex.Section("Introduction")
    section.append("Some prose.")
    for label in labels:
        figure = aastex.Figure(label, position="!htb")
        figure.add_fig(plt.figure(figsize=(1, 1)), width=None)
        figure.add_caption(aastex.NoEscape(r"A caption citing \cadence."))
        section.append(figure)
    result.append(section)

    result.append(aastex.Bibliography("sources"))
    return result


@pytest.fixture(autouse=True)
def _close_figures() -> collections.abc.Iterator[None]:
    """Close the figures each test makes."""
    yield
    plt.close("all")


def test_export_seed(tmp_path: pathlib.Path) -> None:
    """A manuscript with no main file is seeded with all of the prose."""
    written = _export(_document(), tmp_path, names=_names)
    assert all(path.exists() for path in written)

    main = (tmp_path / esis2_science_paper.filename_main).read_text("utf-8")
    assert r"\input{generated/variables}" in main
    assert r"\input{sections/00_abstract}" in main
    assert r"\input{sections/01_introduction}" in main
    assert r"\newcommand{\cadence}" not in main
    assert r"\input{acronyms}" in main
    assert r"\newacro" not in main
    assert r"\bibliography{sources}" in main

    sections = tmp_path / esis2_science_paper.directory_sections
    abstract = (sections / "00_abstract.tex").read_text("utf-8")
    assert r"An abstract citing \cadence." in abstract

    introduction = (sections / "01_introduction.tex").read_text("utf-8")
    assert r"\section{Introduction}" in introduction
    assert r"\includegraphics{generated/test.pdf}" in introduction
    assert r"A caption citing \cadence." in introduction

    generated = tmp_path / esis2_science_paper.directory_generated
    assert (generated / "test.pdf").exists()
    assert (generated / "README.md").exists()
    variables = (generated / esis2_science_paper.filename_variables).read_text("utf-8")
    assert r"\newcommand{\cadence}" in variables

    path = tmp_path / esis2_science_paper.filename_acronyms
    acronyms = path.read_text("utf-8")
    assert "To add one" in acronyms
    # the example in the header is commented out
    assert acronyms.count("\n" + r"\newacro{") == 2
    # each macro is on a line of its own, without pylatex's trailing `%`
    assert "\n" + r"\newcommand{\CTISs}{\acp{CTIS}}" + "\n" in acronyms
    assert "%" not in acronyms.split(r"\newacro{CTIS}")[1]

    assert (tmp_path / "sources.bib").exists()
    assert (tmp_path / "aastex701.cls").exists()
    assert (tmp_path / "aasjournalv7.bst").exists()
    assert (tmp_path / "orcid-ID.png").exists()


def test_export_keeps_prose(tmp_path: pathlib.Path) -> None:
    """
    A manuscript which has a main file keeps its prose, and only the
    generated files are written.
    """
    main = tmp_path / esis2_science_paper.filename_main
    main.write_text("the main file as the authors left it", encoding="utf-8")

    section = tmp_path / esis2_science_paper.directory_sections / "01_introduction.tex"
    section.parent.mkdir()
    section.write_text("an edited section", encoding="utf-8")

    sources = tmp_path / "sources.bib"
    sources.write_text("% the authors' bibliography", encoding="utf-8")

    _export(_document(), tmp_path, names=_names)

    assert main.read_text("utf-8") == "the main file as the authors left it"
    assert section.read_text("utf-8") == "an edited section"
    assert sources.read_text("utf-8") == "% the authors' bibliography"
    assert not (section.parent / "00_abstract.tex").exists()
    assert not (tmp_path / esis2_science_paper.filename_acronyms).exists()

    generated = tmp_path / esis2_science_paper.directory_generated
    assert (generated / "test.pdf").exists()
    assert (generated / esis2_science_paper.filename_variables).exists()


def test_export_removes_stale(tmp_path: pathlib.Path) -> None:
    """The image of a figure which is gone is removed from the manuscript."""
    generated = tmp_path / esis2_science_paper.directory_generated
    generated.mkdir()
    stale = generated / "removed.pdf"
    stale.write_bytes(b"")

    _export(_document(), tmp_path, names=_names)

    assert not stale.exists()
    assert (generated / "test.pdf").exists()


def test_export_names_mismatch(tmp_path: pathlib.Path) -> None:
    """Every section needs the name of a file to be seeded into."""
    with pytest.raises(ValueError, match="2 sections"):
        _export(_document(), tmp_path, names=_names[:1])


def test_export_duplicate_images(tmp_path: pathlib.Path) -> None:
    """Two figures with the same label would overwrite each other's image."""
    with pytest.raises(ValueError, match="two images"):
        _export(_document(("fig:test", "fig:test")), tmp_path, names=_names)
