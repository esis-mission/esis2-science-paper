import pathlib
import shutil
import subprocess

import esis2_science_paper

__all__ = [
    "pdf",
]


def _manuscript() -> pathlib.Path:
    """
    The prose of the article, :data:`esis2_science_paper.directory_manuscript`
    at the root of the repository.

    It is beside this package rather than inside it, so it is found only
    when the package is installed from a checkout of the repository, in
    editable mode.
    """
    result = pathlib.Path(__file__).parent.parent
    result = result / esis2_science_paper.directory_manuscript
    if not (result / esis2_science_paper.filename_main).is_file():
        raise FileNotFoundError(
            f"the manuscript was not found at {result}; the article is built "
            f"from a checkout of the repository, installed with `pip install -e .`"
        )
    return result


def pdf() -> pathlib.Path:
    """
    Build a pdf version of the article and return its path.

    The article is compiled from a copy of the manuscript, into which
    :func:`export` writes the figures and the numbers, in a directory of its
    own. That is what the authors compile in Overleaf after a delivery, so a
    number or a figure the prose cites and the analysis no longer supplies
    fails here first.

    ``latexmk`` is required, since it runs BibTeX and repeats the build
    until the citations and the cross-references are resolved.
    """

    if shutil.which("latexmk") is None:
        raise FileNotFoundError(
            "`latexmk` is needed to build the article, and was not found"
        )

    # Copied afresh every time, so that nothing of an earlier build is left,
    # and without the files of an earlier delivery into the manuscript.
    directory = pathlib.Path(__file__).parent / "build"
    shutil.rmtree(directory, ignore_errors=True)
    shutil.copytree(
        src=_manuscript(),
        dst=directory,
        ignore=shutil.ignore_patterns(esis2_science_paper.directory_generated),
    )

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
