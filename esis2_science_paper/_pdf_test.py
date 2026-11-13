import pathlib

import pymupdf
import pytest

import esis2_science_paper


def test_pdf(capsys: pytest.CaptureFixture) -> None:
    with capsys.disabled():
        pdf = esis2_science_paper.pdf()
    assert isinstance(pdf, pathlib.Path)
    assert pdf.exists()

    # The article is built from a copy of the manuscript with the figures
    # and the numbers delivered into it.
    directory = pdf.parent
    assert (directory / esis2_science_paper.filename_main).exists()
    generated = directory / esis2_science_paper.directory_generated
    assert (generated / esis2_science_paper.filename_variables).exists()

    with pymupdf.open(pdf) as document:
        text = "".join(page.get_text() for page in document)

    # The bibliography and the cross-references are only resolved if the
    # article is compiled repeatedly with BibTeX in between, which `latexmk`
    # does and a bare `pdflatex` does not. Without this check the article
    # builds "successfully" with every citation rendered as `(?)` and no
    # reference list at all.
    assert "(?)" not in text
    assert "??" not in text

    bbl = pdf.with_suffix(".bbl")
    assert bbl.exists()
    assert "bibitem" in bbl.read_text(encoding="utf-8", errors="replace")


def test_manuscript_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A package installed without the repository says why it cannot build."""
    monkeypatch.setattr(esis2_science_paper, "directory_manuscript", "nowhere")
    with pytest.raises(FileNotFoundError, match="pip install -e"):
        esis2_science_paper._pdf._manuscript()
