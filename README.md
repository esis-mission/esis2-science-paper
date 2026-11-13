# esis2-science-paper

[![tests](https://github.com/esis-mission/esis2-science-paper/actions/workflows/tests.yml/badge.svg)](https://github.com/esis-mission/esis2-science-paper/actions/workflows/tests.yml)
[![Black](https://github.com/esis-mission/esis2-science-paper/actions/workflows/black.yml/badge.svg)](https://github.com/esis-mission/esis2-science-paper/actions/workflows/black.yml)
[![Ruff](https://github.com/esis-mission/esis2-science-paper/actions/workflows/ruff.yml/badge.svg)](https://github.com/esis-mission/esis2-science-paper/actions/workflows/ruff.yml)

An AAS journal article describing the second flight of the EUV Snapshot
Imaging Spectrograph (ESIS-II), a sounding rocket computed tomography imaging
spectrograph which will observe an active region in Ne VII 465 Å and
Si XII 499 Å.

Jacob D. Parker, Genevieve D. Vigil, Charles C. Kankelborg, Amy R. Winebarger,
Will T. Barnes, Roy T. Smart, and Adrian N. Daw

📄 **[Read the article (pdf)](https://esis-mission.github.io/esis2-science-paper/esis2-science.pdf)**

## What this is

The article follows the structure of the ESIS-II proposal in three parts:

- **Scientific motivation for the passband.** Electron beams accelerated by
  coronal reconnection heat active region moss, and blue-shift its transition
  region lines in a way that heating by conduction does not. Ne VII responds
  to beam heating in the same way, and Si XII images the extended coronal
  loops that are the hardest structures for a CTIS to invert.
- **The ESIS-II instrument**, mostly in terms of what has changed since the
  first flight: the passband, the optics, two more channels, and the
  mechanical layout. The design has changed considerably since the proposal,
  so the instrument is described from the current model in
  [`esis`](https://github.com/esis-mission/esis) (`esis.flights.f2`), not from
  the proposal.
- **Inversions of test data**, to find how many channels are needed to
  recover the line profiles of extended structures.

## This repository *is* the article

The prose of the article is LaTeX, in the `manuscript` directory, which is a
copy of the Overleaf project the authors edit it in. Every figure and numeric
value in the prose is computed at build time by the `esis2_science_paper`
package, so the text cannot drift away from the analysis. Numbers reach the
prose as macros rather than as literals; a quantity the analysis has not
produced yet is rendered as a bold **XX**. Sections not yet written appear in
the PDF as a gray outline.

```python
import esis2_science_paper
esis2_science_paper.pdf()
```

| path | contents |
|---|---|
| `manuscript/` | the prose: the main file, the acronyms, a file per section, and the bibliography |
| `esis2_science_paper/figures/` | one module per figure, each returning an `aastex.Figure` holding its image |
| `esis2_science_paper/_variables.py` | the `aastex.Variable` macros quoted in the prose |
| `esis2_science_paper/_export.py` | writes the figures and the numbers into a manuscript |
| `esis2_science_paper/_pdf.py` | compiles the manuscript with them |

The analysis itself belongs in the group's libraries, not here:
[`esis`](https://github.com/esis-mission/esis) for the instrument model and
the synthetic scenes, and [`ctis`](https://github.com/sun-data/ctis) for the
inversions.

## Building

Requires Python 3.12 or newer and a LaTeX installation. On Ubuntu:

```bash
sudo apt-get install latexmk texlive-publishers texlive-science cm-super
```

`latexmk` is not optional. Without it `pylatex` falls back to a single
`pdflatex` pass, which silently produces an article with no bibliography.

```bash
pip install -e .[test]
pytest                       # builds and validates the pdf
black esis2_science_paper    # formatting, enforced in CI
ruff check                   # linting, enforced in CI
```

## Continuous integration

Every push runs the test suite, which builds the article and checks that no
citation or cross-reference is left unresolved. Pushes to `main` publish the
article to the link above, and pull requests get their own preview at
`…/pr/<number>/esis2-science.pdf`, linked in a comment on the pull request and
removed when it closes.

## Editing the prose

The prose can be edited in two places, and each is kept up to date with the
other by the `manuscript` workflow:

- **In Overleaf**, where the authors write. Every night, the prose of the
  Overleaf project is copied into a pull request here. The workflow can also
  be run by hand from the Actions tab, to bring edits in sooner.
- **In `manuscript/` here**, through a pull request. When it is merged, its
  changes are merged into the Overleaf project, beside whatever the authors
  have edited there since.

The two layouts are the same: `manuscript/sections/01_introduction.tex` here
is `sections/01_introduction.tex` in Overleaf.

An edit here and an edit in Overleaf to different lines of a file are both
kept. If they change the same lines, nothing is sent to Overleaf and the
workflow fails. Run it by hand to open a pull request with the prose of
Overleaf, settle the lines there, and merge it.

GitHub does not start the checks of a pull request a workflow opens, so the
workflow starts them itself. The repository setting "Allow GitHub Actions to
create and approve pull requests" has to be on for it to open one.

## Figures and numbers

The parts of the manuscript which come from the analysis are not kept in
`manuscript/`. `export()` writes them into a copy of it:

```python
import esis2_science_paper
esis2_science_paper.export("path/to/overleaf")
```

| path | contents |
|---|---|
| `generated/variables.tex` | a `\newcommand` for every number the prose cites |
| `generated/<figure>.pdf` | the image of each figure |
| `aastex701.cls`, `aasjournalv7.bst`, `orcid-ID.png` | the AASTeX class files |

`pdf()` and the tests compile `manuscript/` with them, so a number or a figure
the prose cites and the analysis no longer supplies fails a pull request.

Publishing a release runs the `overleaf` workflow, which writes them into the
Overleaf project, replacing those of the last release, pushes one commit, and
attaches the whole manuscript to the release. It can be run by hand to
deliver without cutting a version. Everything in `generated/` is replaced on
every delivery, so it is the one part of the Overleaf project not to edit by
hand.

To add a figure, write its module in `figures/`, add it to
`figures.figures()`, and add its `figure` environment, with
`\includegraphics{generated/<name>}` and its caption, to a section in
`manuscript/`.

Both workflows need two repository secrets, and warn and skip without them:

| Secret | Value |
|---|---|
| `OVERLEAF_TOKEN` | A git authentication token from Overleaf's account settings |
| `OVERLEAF_PROJECT_ID` | The part of the project's URL after `overleaf.com/project/` |

## Commenting on the draft

Each author has a colored comment macro for notes in the prose:
`\jake{...}`, `\genevieve{...}`, `\charles{...}`, `\amy{...}`, `\will{...}`,
`\roy{...}`, and `\adrian{...}`.
