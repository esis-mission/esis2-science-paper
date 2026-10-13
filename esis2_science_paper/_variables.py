import aastex
import num2words
import pylatex

import esis2_science_paper

__all__ = [
    "variables",
]


def _pending(name: str) -> aastex.Variable:
    """
    A quantity the analysis has not produced yet, marked where it is cited.

    Every number in this article is computed by the analysis, and these are
    the ones it has no answer for yet. They are written into the text as a
    bold ``XX`` rather than guessed at or left out, so that a draft shows
    plainly what is still owed and no placeholder can be mistaken for a
    measurement. ``??`` is avoided since it is what LaTeX prints for an
    unresolved cross-reference, which the tests look for.
    """
    return aastex.Variable(name=name, value=aastex.NoEscape(r"\textbf{XX}"))


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the analysis.
    """
    return [
        aastex.Variable(
            # the number of emission lines drawn in the bunch figure
            name="numEmissionLines",
            value=aastex.NoEscape(
                num2words.num2words(esis2_science_paper.figures.num_emission_lines)
            ),
        ),
        aastex.Variable(
            # the pressure the active region spectrum is computed at
            name="chiantiPressure",
            value=esis2_science_paper._spectrum.pressure,
        ),
        aastex.Variable(
            # The files the spectrum was computed from, named rather than
            # described, so that the article says which of the several
            # abundance tables and several differential emission measures
            # CHIANTI carries were the ones read.
            name="chiantiAbundances",
            # `Command` escapes its argument, which these names need: an
            # underscore outside of mathematics is a subscript and does not
            # compile, and every one of these file names has several.
            value=aastex.NoEscape(
                pylatex.Command(
                    "texttt",
                    esis2_science_paper._spectrum.abundance,
                ).dumps()
            ),
        ),
        aastex.Variable(
            name="chiantiDEM",
            value=aastex.NoEscape(
                pylatex.Command(
                    "texttt",
                    esis2_science_paper._spectrum.dem,
                ).dumps()
            ),
        ),
        aastex.Variable(
            # Read from the database rather than written down, since which
            # version is installed is what the numbers were computed from,
            # and the two would otherwise drift apart silently.
            name="chiantiVersion",
            value=aastex.NoEscape(esis2_science_paper._spectrum.version()),
        ),
        # the formation temperatures of the two lines, from CHIANTI
        _pending("temperatureNeVII"),
        _pending("temperatureSiXII"),
        # from the ESIS-II optical model in `esis.flights.f2`
        _pending("fieldOfView"),
        _pending("cadence"),
        # from the inversions of the test data
        _pending("numChannelsRequired"),
        _pending("velocityError"),
    ]
