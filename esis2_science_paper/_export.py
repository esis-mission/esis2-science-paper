import importlib.metadata
import pathlib
import re
import shutil

import aastex
import pylatex

import esis2_science_paper

__all__ = [
    "export",
]

_filename_sources = "sources.bib"
"""The bibliography of the manuscript, seeded from the one in this package."""

_header_acronyms = r"""% The acronyms of the article, for the acronym package.
%
% Each one is declared with \newacro, and has a macro for its usual form,
% such as \CTIS, which is spelled out the first time it is used and
% abbreviated after that, and one for the start of a sentence, such as
% \CTISCapital. Some also have a plural, \CTISs and \CTISCapitals, or a
% macro which is always abbreviated, \ARShort.
%
% To add one, copy an entry and change its name and its expansion:
%
% \newacro{EIS}[EIS]{the EUV Imaging Spectrometer}
% \newcommand{\EIS}{\ac{EIS}}
% \newcommand{\EISCapital}{\Ac{EIS}}
"""
"""The first lines of the acronyms file, which say how to add one."""


def _dumps_acronym(acronym: aastex.Acronym) -> str:
    r"""
    The definition of one acronym, with each of its macros on a line of its
    own, so that it can be read and edited by hand.

    Parameters
    ----------
    acronym
        The acronym to define.
    """
    tex = acronym.dumps().removesuffix("%")
    return tex.replace(r"}\newcommand", "}\n\\newcommand")


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
preamble, and `{sources}`, belongs to this project and is never overwritten.
"""
"""The README of :data:`esis2_science_paper.directory_generated`, for the authors in Overleaf."""


def _version() -> str:
    """The version of this package, which names the delivery."""
    return importlib.metadata.version("esis2-science-paper")


def _relocate_images(tex: str, document: aastex.Document) -> str:
    r"""
    Point the ``\includegraphics`` commands of some LaTeX at the images
    inside :data:`esis2_science_paper.directory_generated` instead of beside the main file.

    Parameters
    ----------
    tex
        LaTeX taken from ``document``.
    document
        The document whose images are moved.
    """
    for image in document.images:
        name = re.escape(image.name)
        tex = re.sub(
            pattern=rf"(\\includegraphics(?:\[[^\]]*\])?)\{{{name}\}}",
            repl=rf"\1{{{esis2_science_paper.directory_generated}/{image.name}}}",
            string=tex,
        )
    return tex


def _write_generated(
    document: aastex.Document,
    directory: pathlib.Path,
) -> list[pathlib.Path]:
    """
    Write the files this package owns into the manuscript, replacing any
    left by an earlier delivery.

    Parameters
    ----------
    document
        The article.
    directory
        The root of the manuscript.
    """
    generated = directory / esis2_science_paper.directory_generated
    generated.mkdir(parents=True, exist_ok=True)

    # A figure which has since been removed or renamed would otherwise leave
    # its image behind.
    for path in generated.iterdir():
        if path.is_file():
            path.unlink()

    written = []

    seen = {}
    for image in document.images:
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
    lines = [variable.dumps() for variable in document.variables]
    path = generated / esis2_science_paper.filename_variables
    path.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")
    written.append(path)

    for source in document.class_files:
        path = directory / source.name
        shutil.copyfile(source, path)
        written.append(path)

    path = generated / "README.md"
    readme = _readme.format(
        version=_version(),
        variables=esis2_science_paper.filename_variables,
        generated=esis2_science_paper.directory_generated,
        class_files=", ".join(f"`{f.name}`" for f in document.class_files),
        sources=_filename_sources,
    )
    path.write_text(readme, encoding="utf-8")
    written.append(path)

    return written


def _write_seed(
    document: aastex.Document,
    directory: pathlib.Path,
    names: tuple[str, ...],
) -> list[pathlib.Path]:
    r"""
    Write the prose of the article into the manuscript as the files its
    authors edit from then on.

    The main file keeps the preamble, the title, the authors, and the
    keywords, and includes each section from a file of its own, with its
    figures and their captions, and the acronyms from
    :data:`esis2_science_paper.filename_acronyms`.
    The macros of the numbers are read from
    :data:`esis2_science_paper.directory_generated`, and the figures
    include their images from there.

    This changes ``document``, so it is written after the generated files,
    which are taken from it unchanged.

    Parameters
    ----------
    document
        The article.
    directory
        The root of the manuscript.
    names
        The name of the file each section is written to, in order.
    """
    parts = [
        index
        for index, item in enumerate(document.data)
        if isinstance(item, (aastex.Section, aastex.Abstract))
    ]
    if len(parts) != len(names):
        raise ValueError(
            f"the article has {len(parts)} sections, counting the abstract, "
            f"but {len(names)} names were given for their files: {names}"
        )

    written = []

    sections = directory / esis2_science_paper.directory_sections
    sections.mkdir(parents=True, exist_ok=True)
    for index, name in zip(parts, names):
        tex = _relocate_images(document.data[index].dumps(), document)
        path = sections / f"{name}.tex"
        path.write_text(tex.strip("\n") + "\n", encoding="utf-8")
        written.append(path)
        document.data[index] = pylatex.NoEscape(
            rf"\input{{{esis2_science_paper.directory_sections}/{name}}}"
        )

    acronyms = [
        index
        for index, item in enumerate(document.preamble)
        if isinstance(item, aastex.Acronym)
    ]
    if acronyms:
        entries = [_dumps_acronym(document.preamble[i]) for i in acronyms]
        path = directory / esis2_science_paper.filename_acronyms
        tex = _header_acronyms + "\n" + "\n\n".join(entries) + "\n"
        path.write_text(tex, encoding="utf-8")
        written.append(path)
        stem = pathlib.Path(esis2_science_paper.filename_acronyms).stem
        document.preamble[acronyms[0]] = pylatex.NoEscape(rf"\input{{{stem}}}")
        for index in reversed(acronyms[1:]):
            del document.preamble[index]

    stem = pathlib.Path(esis2_science_paper.filename_variables).stem
    document.variables = [
        pylatex.NoEscape(
            rf"\input{{{esis2_science_paper.directory_generated}/{stem}}}"
        ),
    ]

    path = directory / esis2_science_paper.filename_main
    tex = _relocate_images(document.dumps(), document)
    path.write_text(tex.strip("\n") + "\n", encoding="utf-8")
    written.append(path)

    path = directory / _filename_sources
    shutil.copyfile(pathlib.Path(__file__).parent / _filename_sources, path)
    written.append(path)

    return written


def _export(
    document: aastex.Document,
    directory: str | pathlib.Path,
    names: None | tuple[str, ...] = None,
) -> list[pathlib.Path]:
    """
    Write a document into a manuscript, seeding the prose only if the
    manuscript has none yet.

    Parameters
    ----------
    document
        The article.
    directory
        The root of the manuscript.
    names
        The name of the file each section is seeded into, in order.
        If :obj:`None`, :data:`esis2_science_paper.names_sections`.
    """
    if names is None:
        names = esis2_science_paper.names_sections

    directory = pathlib.Path(directory)
    directory.mkdir(parents=True, exist_ok=True)

    seed = not (directory / esis2_science_paper.filename_main).exists()

    written = _write_generated(document, directory)
    if seed:
        written += _write_seed(document, directory, names)

    return written


def export(directory: str | pathlib.Path) -> list[pathlib.Path]:
    r"""
    Deliver the article into a copy of its manuscript, such as a clone of
    the Overleaf project.

    The prose of the article, its captions included, belongs to the
    manuscript, where the authors edit it, so it is written only once, to
    seed a manuscript which does not have a main file yet,
    :data:`esis2_science_paper.filename_main`.
    Every delivery writes the parts which come from the analysis into
    :data:`esis2_science_paper.directory_generated`, replacing those of the last: the image of
    each figure, and the macro of every number the prose cites.
    The AASTeX class files are written beside the main file each time too.

    Parameters
    ----------
    directory
        The root of the manuscript, where its main file is.

    Returns
    -------
    The files that were written.
    """
    return _export(esis2_science_paper.document(), directory)
