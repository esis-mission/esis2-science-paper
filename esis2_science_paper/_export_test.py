import pathlib

import aastex
import matplotlib.pyplot as plt
import pytest

import esis2_science_paper


@pytest.fixture(autouse=True)
def _close_figures() -> None:
    yield
    plt.close("all")


def _figure(label: str) -> aastex.Figure:
    """A figure with one image, named after its label."""
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1])
    result = aastex.Figure(label)
    result.add_fig(fig, width=None)
    return result


def _variables() -> list[aastex.Variable]:
    return [aastex.Variable(name="cadence", value=3)]


def _export(directory: pathlib.Path, labels: list[str]) -> list[pathlib.Path]:
    return esis2_science_paper._export._export(
        figures=[_figure(label) for label in labels],
        variables=_variables(),
        directory=directory,
    )


def test_export(tmp_path: pathlib.Path) -> None:
    """The images, the numbers, and the class files are written."""
    written = _export(tmp_path, ["fig:one", "fig:two"])
    assert all(path.is_file() for path in written)

    generated = tmp_path / esis2_science_paper.directory_generated
    assert (generated / "one.pdf").is_file()
    assert (generated / "two.pdf").is_file()
    assert (generated / "README.md").is_file()

    variables = generated / esis2_science_paper.filename_variables
    assert r"\cadence" in variables.read_text(encoding="utf-8")

    assert list(tmp_path.glob("*.cls"))


def test_export_keeps_prose(tmp_path: pathlib.Path) -> None:
    """A delivery does not touch the prose of the manuscript."""
    main = tmp_path / esis2_science_paper.filename_main
    main.write_text("the prose", encoding="utf-8")
    section = tmp_path / "sections" / "01_introduction.tex"
    section.parent.mkdir()
    section.write_text("an introduction", encoding="utf-8")

    _export(tmp_path, ["fig:one"])

    assert main.read_text(encoding="utf-8") == "the prose"
    assert section.read_text(encoding="utf-8") == "an introduction"


def test_export_removes_stale(tmp_path: pathlib.Path) -> None:
    """The image of a figure which was removed is not left behind."""
    generated = tmp_path / esis2_science_paper.directory_generated
    _export(tmp_path, ["fig:one", "fig:two"])
    _export(tmp_path, ["fig:one"])
    assert (generated / "one.pdf").is_file()
    assert not (generated / "two.pdf").exists()


def test_export_duplicate_images(tmp_path: pathlib.Path) -> None:
    """Two figures with one label would write one image over the other."""
    with pytest.raises(ValueError, match="two images are named"):
        _export(tmp_path, ["fig:one", "fig:one"])
