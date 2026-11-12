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

Every figure, table, and numeric value in the prose is computed at build time
by the `esis2_science_paper` package, so the text cannot drift away from the
analysis. Numbers reach the prose as `aastex.Variable` macros rather than as
literals; a quantity the analysis has not produced yet is rendered as a bold
**XX**. Sections not yet written appear in the PDF as a gray outline.

```python
import esis2_science_paper
esis2_science_paper.pdf()
```

| path | contents |
|---|---|
| `_document.py` | assembles the article and renders the pdf |
| `sections/` | the prose, as LaTeX strings, one module per section |
| `figures/` | one module per figure, each returning an `aastex.Figure` |
| `tables/` | one module per table |
| `_variables.py` | the `aastex.Variable` macros quoted in the prose |
| `_acronyms.py` | acronym definitions used as `\ACRONYM` macros |
| `_preamble.py` | custom commands, including a comment macro per author |
| `sources.bib` | the bibliography |

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

## Editing in Overleaf

The authors edit the prose of the article in Overleaf, and this repository
delivers the parts of it which come from the analysis there on every
release.

```python
import esis2_science_paper
esis2_science_paper.export("path/to/overleaf")
```

`export()` writes into a clone of the Overleaf project:

| path | written | contents |
|---|---|---|
| `generated/variables.tex` | every release | a `\newcommand` for every number the prose cites |
| `generated/<figure>.pdf` | every release | the image of each figure |
| `aastex701.cls`, `aasjournalv7.bst`, `orcid-ID.png` | every release | the AASTeX class files |
| `esis2-science.tex` | once | the main file: the preamble, title, authors, and keywords |
| `sections/<name>.tex` | once | each section, with its figures and their captions |
| `sources.bib` | once | the bibliography |

The files written once seed a project which does not have
`esis2-science.tex` yet, and are never written again, so from then on the
prose, the captions, the macros of the preamble, and the bibliography belong
to Overleaf. Edit them there: a change to the prose in this repository does
not reach the manuscript once it is seeded. Everything in `generated/` is
replaced on every delivery, so it is the one part of the manuscript not to
edit by hand. A number the prose cites, or a figure, is changed here and
reaches the manuscript with the next release.

### Delivery

Publishing a release runs the `overleaf` workflow, which exports the
article into the Overleaf project, pushes it as a single commit, and
attaches the exported manuscript to the release. The same workflow can be
run by hand from the Actions tab to deliver without cutting a version.

It needs two repository secrets, and warns and skips the push without them:

| Secret | Value |
|---|---|
| `OVERLEAF_TOKEN` | A git authentication token from Overleaf's account settings |
| `OVERLEAF_PROJECT_ID` | The part of the project's URL after `overleaf.com/project/` |

The project is cloned fresh every time, since Overleaf refuses a push that
is not a fast-forward. After the first delivery seeds it, set its main
document to `esis2-science.tex` (Menu, then Main document), and delete the
`main.tex` a new Overleaf project starts with.

## Commenting on the draft

Each author has a colored comment macro for notes in the prose:
`\jake{...}`, `\genevieve{...}`, `\charles{...}`, `\amy{...}`, `\will{...}`,
`\roy{...}`, and `\adrian{...}`.
