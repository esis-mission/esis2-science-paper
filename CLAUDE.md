# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`esis2-science-paper` is a **reproducible scientific article**, not a conventional
software library. Its prose is LaTeX in `manuscript/`, and the `esis2_science_paper`
Python package computes every figure and numeric value the prose cites, for
the second flight of the EUV Snapshot Imaging Spectrograph (ESIS-II).
Calling `esis2_science_paper.pdf()` produces the final `esis2-science.pdf`.

The authors edit the prose in **Overleaf**, and `manuscript/` is a copy of the
Overleaf project. Edits flow both ways; see **Overleaf** below.

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
- **Every number in the prose is an `aastex.Variable`** defined in `_variables.py`,
  cited in the prose by its macro. A number the analysis cannot supply yet is
  declared with `_pending()`, which renders as a bold `XX`, so the draft shows
  plainly what is still owed.
- Sections not yet written are drafted as an `outline` environment (defined in
  the preamble of `manuscript/esis2-science.tex`), which renders as a gray
  bulleted list, so the plan cannot be mistaken for the article.

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

- **`manuscript/`** (at the root of the repository): the prose.
  `esis2-science.tex` is the main file (preamble, custom commands such as
  `\ESISII` and `\NeVII`, a colored comment macro per author, title, authors,
  keywords), `acronyms.tex` defines the `\ACRONYM` macros, `sections/NN_<name>.tex`
  holds each section with its `figure` environments and captions, and
  `sources.bib` is the bibliography. `manuscript/generated/` and the AASTeX
  class files are written by `export()` and are gitignored.
- **`figures/`**: each module builds a matplotlib figure and wraps it in an
  `aastex.Figure`/`FigureStar`, which names its image after its label
  (`fig:bunch` is `generated/bunch.pdf`). `figures.figures()` lists them all.
  The `figure` environment and the caption are in `manuscript/`.
- **`_variables.py`**: `aastex.Variable` LaTeX macros for every numeric value
  cited in the prose.
- **`_export.py`**: `export(directory)` writes `generated/` (the image of each
  figure, `variables.tex`, a README for the authors) and the class files into
  a copy of the manuscript, replacing those of the last delivery. It never
  touches the prose.
- **`_pdf.py`**: `pdf()` copies `manuscript/` into `esis2_science_paper/build/`,
  exports into it, and compiles with `latexmk`. It finds `manuscript/` beside
  the package, so the package must be installed in editable mode.
- **`_spectrum.py`**: the CHIANTI spectrum of an active region (via `utu` and
  `fiasco`), the contribution functions of single lines and the temperatures
  they peak at, and the effective area of one ESIS-II channel. All are slow, so
  all are cached with `esis.memory`, keyed on the CHIANTI, `optika`, and `esis`
  versions. `joblib` keys only on a function's arguments and source, so pass
  every module-level setting (abundances, DEM, pressure) into a cached function
  rather than reading it there, or changing it serves stale results. Pass
  arguments every computer computes alike: an exponent grid rather than
  `10 ** grid`, since NumPy's `power` uses SVML on AVX-512 runners and libm on
  others, and the last bit, hence the key, differs between them.
  CI caches `~/.fiasco` under its version. What the article computes (this
  package's `joblib` results, those of the `esis` scene, and the AIA images and
  JSOC searches) is a rolling cache: `.github/actions/setup` restores the newest
  one, and `.github/actions/remember` saves a new one only if the run wrote a
  file into it.
  A result too slow for a runner is computed on a workstation and given to
  the cache by `.github/workflows/seed.yml`, from an archive of
  `~/.esis/cache` attached to a draft release. `joblib` keys are the same on
  Windows and Linux, but only if the workstation has the versions of the
  packages the runner installs.

## Overleaf

- **Prose flows both ways**, through `.github/workflows/manuscript.yml`.
  - From Overleaf: nightly or by hand, it copies the Overleaf project's prose
    over `manuscript/` on the branch `overleaf/sync` and opens a pull request,
    then starts `tests`, `ruff`, and `black` on it, since GitHub starts no
    checks for a pull request a workflow opens.
  - To Overleaf: on a push to `main` which changes `manuscript/`,
    `.github/scripts/send-manuscript.sh` merges each changed file three ways
    (before the push, after it, and Overleaf's current copy) and pushes the
    result. A conflict fails the run and sends nothing; settle it in a sync
    pull request.
- **Figures and numbers flow one way**, on a release (or by hand), through
  `.github/workflows/overleaf.yml`: it clones the project, runs `export()`
  into the clone, attaches the manuscript to the release, and pushes one
  commit.
- Both use the `OVERLEAF_TOKEN` and `OVERLEAF_PROJECT_ID` secrets and share a
  concurrency group. `.github/actions/setup` holds the LaTeX, Python, and
  CHIANTI setup `overleaf.yml` shares with `tests.yml`.
- To edit prose from here, edit the `.tex` files in `manuscript/` in a pull
  request. A new figure needs its module, an entry in `figures.figures()`, and
  its `figure` environment in a section of `manuscript/`.
- A renamed or removed `aastex.Variable` breaks any prose which still cites
  it. `test_pdf` compiles the manuscript, so it fails here first; rename the
  macro in `manuscript/` in the same pull request.

## Conventions

- Every module declares an explicit `__all__` and exposes functionality through small
  factory functions, re-exported up the package via `__init__.py`. To add a new
  figure: create `_name.py`, then add it to `figures/__init__.py`.
- Modules import the top-level package as `import esis2_science_paper` and reach back
  into it (`esis2_science_paper.figures.x()`) rather than deep relative imports.
- House style: `Figure~\ref`, `Section~\ref`, `Table~\ref`; `\eg,` with a comma;
  a tie `~` before every `\citep`.
- Cite only entries in `manuscript/sources.bib`, and add new ones from the publisher's
  record (e.g. `curl -LH "Accept: application/x-bibtex" https://doi.org/<doi>`)
  rather than typing them by hand.
- Generated LaTeX/PDF output and caches are gitignored; never commit build artifacts.
- Stage explicit files with `git add`; never `git add` whole directories.
