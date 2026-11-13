import importlib.metadata
import pathlib
import shutil

import aastex
import matplotlib.pyplot as plt

import esis2_science_paper

__all__ = [
    "export",
]

_readme = """\
# Generated files

The files in this directory are written by
[esis2-science-paper](https://github.com/esis-mission/esis2-science-paper)
{version} from the model of ESIS-II, and are replaced on every release of it.
Edit them there instead of here, or the change will be lost.

- `{variables}` defines a macro for every number the prose cites, such as
  `\\cadence`. A number the analysis has not produced yet is a bold **XX**.
- Each image is the figure of the same name, included by a `figure`
  environment in the prose with `\\includegraphics{{{generated}/<name>}}`.

The AASTeX class files at the root of the project, {class_files}, are
replaced on every release too.

Everything else, the prose, the captions, the acronyms, the macros of the
preamble, and the bibliography, is yours to edit here. The repository keeps a
copy of it in its `manuscript` directory: your edits are brought into that
copy, and edits made to that copy are merged into this project.
"""
"""The README of :data:`esis2_science_paper.directory_generated`, for the authors in Overleaf."""


def _version() -> str:
    """The version of this package, which names the delivery."""
    return importlib.metadata.version("esis2-science-paper")


def _export(
    figures: list[aastex.Figure],
    variables: list[aastex.Variable],
    directory: str | pathlib.Path,
) -> list[pathlib.Path]:
    """
    Write the files this package owns into a manuscript, replacing any left
    by an earlier delivery.

    Parameters
    ----------
    figures
        The figures whose images are written.
    variables
        The numbers whose macros are written.
    directory
        The root of the manuscript.
    """
    directory = pathlib.Path(directory)
    class_files = aastex.Document().class_files

    generated = directory / esis2_science_paper.directory_generated
    generated.mkdir(parents=True, exist_ok=True)

    # A figure which has since been removed or renamed would otherwise leave
    # its image behind.
    for path in generated.iterdir():
        if path.is_file():
            path.unlink()

    written = []

    seen = {}
    images = [image for figure in figures for image in figure.images]
    for image in images:
        if image.name in seen:
            raise ValueError(
                f"two images are named {image.name!r}, which usually means "
                f"two figures share the label {pathlib.Path(image.name).stem!r}"
            )
        seen[image.name] = image
        written.append(image.write(generated))

    header = (
        f"% Written by esis2-science-paper {_version()}, and replaced on every\n"
        f"% release of it. Edit the numbers there instead of here.\n"
    )
    lines = [variable.dumps() for variable in variables]
    path = generated / esis2_science_paper.filename_variables
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    written.append(path)

    for source in class_files:
        path = directory / source.name
        shutil.copyfile(source, path)
        written.append(path)

    path = generated / "README.md"
    readme = _readme.format(
        version=_version(),
        variables=esis2_science_paper.filename_variables,
        generated=esis2_science_paper.directory_generated,
        class_files=", ".join(f"`{f.name}`" for f in class_files),
    )
    path.write_text(readme, encoding="utf-8")
    written.append(path)

    return written


def export(directory: str | pathlib.Path) -> list[pathlib.Path]:
    r"""
    Deliver the figures and the numbers of the article into a copy of its
    manuscript, such as a clone of the Overleaf project.

    The prose of the article, its captions included, belongs to the
    manuscript and is not touched. Every delivery writes the parts which
    come from the analysis into :data:`esis2_science_paper.directory_generated`,
    replacing those of the last: the image of each figure, and the macro of
    every number the prose cites. The AASTeX class files are written beside
    the main file each time too.

    Parameters
    ----------
    directory
        The root of the manuscript, where its main file is.

    Returns
    -------
    The files that were written.
    """
    # the figures are set in the typeface of the article
    plt.rcParams["text.usetex"] = True
    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.size"] = 9
    plt.rcParams["lines.linewidth"] = 1

    return _export(
        figures=esis2_science_paper.figures.figures(),
        variables=esis2_science_paper.variables(),
        directory=directory,
    )
