# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`esis2-science-paper` is a **reproducible scientific article**, not a conventional
software library. The `esis2_science_paper` Python package programmatically generates
a complete AAS-journal LaTeX article (text, figures, tables, and numeric values)
describing the second flight of the EUV Snapshot Imaging Spectrograph (ESIS-II).
Calling `esis2_science_paper.pdf()` produces the final `esis2-science.pdf`.

This is one package within the larger Kankelborg-Group workspace (see the parent
`../CLAUDE.md`). Its sibling articles `esis-instrument-paper` (the first flight)
and `esis-jet-paper` follow the same layout and are the templates it was made from.

## The article

The structure parallels the ESIS-II proposal, at Jake Parker's suggestion:

- **Scientific motivation for the passband**: electron beam heating in active
  region moss, why Ne VII 465 Å and Si XII 499 Å, and the requirements.
- **The ESIS-II instrument**, focusing on what has changed since ESIS-I.
- **Inversions of test data**, validating the inversion of extended structures
  (the technology objective) with subsets of the six channels. The test data
  are simulated ESIS-II observations of scenes whose line profiles are known.

The authors are in the order of the science team in the proposal, and Jake
Parker is the corresponding author. The two flights are written with Roman
numerals, ESIS-I and ESIS-II, as in the `esis` package.

## Rules

- **The proposal is stale.** The design has changed considerably since it was
  written. Take the science case from it, but take every design detail and
  number from the current model, `esis.flights.f2` in the `esis` package.
- **Push reusable functionality down the stack**: if a figure or quantity needs a
  capability the libraries lack, add it there (with tests) rather than writing
  bespoke code here. The instrument model belongs in `esis`, the synthetic scenes
  in `esis.data.synth`, and the inversions in `ctis`. This repo should contain only
  prose, `aastex` document assembly, and thin glue that calls library functions.
- **Every number in the prose is an `aastex.Variable`** defined in `_variables.py`.
  A number the analysis cannot supply yet is declared with `_pending()`, which
  renders as a bold `XX`, so the draft shows plainly what is still owed.
- Sections not yet written are drafted as an `outline` environment (defined in
  `_preamble.py`), which renders as a gray bulleted list, so the plan cannot be
  mistaken for the article.

## Commands

Run from this package directory:

```bash
pip install -e .[test]          # install for development
pytest                          # run tests; test_pdf compiles the LaTeX → PDF
black esis2_science_paper       # format (CI enforces --check)
ruff check                      # lint (CI enforces)
```

Building the PDF requires a **LaTeX installation** with `latexmk` (TeX Live:
`texlive-publishers texlive-science cm-super latexmk`). Without `latexmk`,
`pylatex` falls back to a single `pdflatex` pass and the bibliography is
silently missing; `test_pdf` checks for this.

## Architecture

The whole article is assembled in `_document.py`: `document()` builds an
`aastex.Document`, appending acronyms, variables, title, authors, abstract,
keywords, each section, and finally the bibliography (`sources.bib`). `pdf()`
renders it.

- **`sections/`**: each module returns an `aastex.Section` (or `aastex.Abstract`).
  Prose lives here as raw LaTeX strings (with `\cite`, `\ref`, equations) and
  embeds figures/tables by calling the corresponding factory.
- **`figures/`**: each module builds a matplotlib figure and wraps it in an
  `aastex.Figure`/`FigureStar` with a caption.
- **`tables/`**: factories returning `aastex.Table` objects.
- **`_variables.py`**: `aastex.Variable` LaTeX macros for every numeric value
  cited in the prose.
- **`_acronyms.py`**: `aastex.Acronym` definitions; prose uses `\ACRONYM` macros.
- **`_preamble.py`**: custom commands: `\ESISI` and `\ESISII` for the two
  flights, ion macros such as `\NeVII`, and a colored comment macro per author
  (`\jake`, `\genevieve`, `\charles`, `\amy`, `\will`, `\roy`, `\adrian`).

## Conventions

- Every module declares an explicit `__all__` and exposes functionality through small
  factory functions, re-exported up the package via `__init__.py`. To add a new
  figure/table/section: create `_name.py`, then add it to the subpackage `__init__.py`.
- Modules import the top-level package as `import esis2_science_paper` and reach back
  into it (`esis2_science_paper.figures.x()`) rather than deep relative imports.
- House style: `Figure~\ref`, `Section~\ref`, `Table~\ref`; `\eg,` with a comma;
  a tie `~` before every `\citep`.
- Cite only entries in `sources.bib`, and add new ones from the publisher's
  record (e.g. `curl -LH "Accept: application/x-bibtex" https://doi.org/<doi>`)
  rather than typing them by hand.
- Generated LaTeX/PDF output and caches are gitignored; never commit build artifacts.
- Stage explicit files with `git add`; never `git add` whole directories.
