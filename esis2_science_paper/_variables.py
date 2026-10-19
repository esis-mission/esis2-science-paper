import aastex
import astropy.units as u
import esis
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


def _temperature_formation(ion: str, wavelength: u.Quantity) -> u.Quantity:
    """
    The temperature a line is formed at, in megakelvin, to one significant
    figure.

    CHIANTI tabulates the ionization fractions a twentieth of a decade
    apart, and :mod:`fiasco` interpolates between them with a curve which
    flattens at each extremum, so the peak falls on or beside one of them.
    That places it to within about six percent, and a second figure would
    claim more than that.
    """
    result = esis2_science_paper._spectrum.temperature_formation(ion, wavelength)
    result = result.to(u.MK)
    return float(f"{result.value:.1g}") * u.MK


def variables() -> list[aastex.Variable]:
    """
    A list of LaTeX variables for every numeric quantity cited in the prose.

    Reference these macros in section strings instead of hardcoding numbers so
    that the text stays in sync with the analysis.
    """
    return [
        aastex.Variable(
            # the number of emission lines the bunch figure labels by their
            # radiance, and again by the light they put on the detector
            name="numEmissionLines",
            value=aastex.NoEscape(
                num2words.num2words(esis2_science_paper.figures.num_emission_lines)
            ),
        ),
        aastex.Variable(
            # the number of emission lines drawn in the bunch figure
            name="numLinesLabeled",
            value=aastex.NoEscape(
                num2words.num2words(
                    esis2_science_paper.figures.lines_labeled().shape["line"]
                )
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
        # the temperatures the lines are formed at, the peaks of their
        # contribution functions
        aastex.Variable(
            name="temperatureNeVII",
            value=_temperature_formation(
                ion="Ne 7",
                wavelength=esis2_science_paper._spectrum.wavelength_ne_vii,
            ),
        ),
        aastex.Variable(
            name="temperatureSiXII",
            value=_temperature_formation(
                ion="Si 12",
                wavelength=esis2_science_paper._spectrum.wavelength_si_xii,
            ),
        ),
        aastex.Variable(
            name="temperatureSiIV",
            value=_temperature_formation(
                ion="Si 4",
                wavelength=esis2_science_paper._spectrum.wavelength_si_iv,
            ),
        ),
        # the scene of the simulated image
        aastex.Variable(
            name="numLinesScene",
            value=aastex.NoEscape(
                num2words.num2words(
                    esis2_science_paper._synthetic.wavelength_synthetic().size
                )
            ),
        ),
        aastex.Variable(
            name="fractionLineMin",
            value=aastex.NoEscape(
                rf"{100 * esis2_science_paper._synthetic.fraction_min:g}\%"
            ),
        ),
        aastex.Variable(
            name="sizeBlock",
            value=esis2_science_paper._synthetic.size_block,
        ),
        # from the ESIS-II optical model in `esis.flights.f2`
        aastex.Variable(
            name="timeExposure",
            value=esis.flights.f2.optics.design_single(
                num_distribution=0,
            ).camera.timedelta_exposure,
        ),
        _pending("fieldOfView"),
        _pending("cadence"),
        # from the inversions of the test data
        _pending("numChannelsRequired"),
        _pending("velocityError"),
    ]
