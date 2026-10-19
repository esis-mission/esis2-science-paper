import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import matplotlib.text
import named_arrays as na
import numpy as np
import utu

import esis2_science_paper

__all__ = [
    "bunch",
    "lines_detected",
    "num_emission_lines",
]

_num_wavelength = 51
"""The number of wavelengths at which the effective area is computed."""

num_emission_lines = 8
"""The number of emission lines to label."""

_color_area = "red"
"""The colour of the effective area curve."""

_headroom = 1.45
"""How much taller than the brightest line the axes are, to leave room for the labels."""


def _passband() -> tuple[u.Quantity, u.Quantity]:
    """The shortest and the longest wavelength of the passband."""
    optics = esis.flights.f2.optics.design_single(num_distribution=0)
    return (
        optics.wavelength_min.to(u.AA).ndarray,
        optics.wavelength_max.to(u.AA).ndarray,
    )


def _wavelength() -> na.AbstractScalar:
    """The wavelengths across the passband at which the effective area is computed."""
    wavelength_min, wavelength_max = _passband()
    return na.linspace(
        start=wavelength_min,
        stop=wavelength_max,
        axis="wavelength",
        num=_num_wavelength,
    )


def lines_detected() -> na.FunctionArray:
    """
    The :data:`num_emission_lines` lines of the passband which put the most
    light on the detector, most first.

    Their radiance times the effective area at their wavelength is greatest.
    The coatings reflect little at the short end of the passband, so some of
    its brightest lines are hardly detected, while fainter lines near the peak
    of the effective area are among the brightest in a simulated image.
    """
    wavelength_min, wavelength_max = _passband()
    lines = esis2_science_paper.lines(
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
    )

    wavelength = _wavelength()
    area = esis2_science_paper._spectrum.area_effective(wavelength)

    # The effective area at the wavelength of each line, interpolated from
    # the curve, which is smooth over the two angstroms between its samples.
    area_line = na.interp(
        x=lines.inputs.components["wavelength"],
        xp=wavelength,
        fp=area,
        axis="wavelength",
    )

    signal = lines.outputs * area_line
    index = np.argsort(-signal, axis="line")
    index = index["line"][{"line": slice(num_emission_lines)}]

    return lines[{"line": index}]


def bunch() -> aastex.FigureStar:
    r"""
    The lines which put the most light on the detector, and the effective
    area beneath them.

    The lines are computed from the CHIANTI atomic database for an active
    region, and the effective area from the instrument model with the
    apertures of the filter and the sensor opened, so that the curve is the
    response of the coatings and the filter rather than a map of where the
    light happens to land. The lines are those of :func:`lines_detected`.
    """
    wavelength_min, wavelength_max = _passband()

    wavelength = _wavelength()
    area = esis2_science_paper._spectrum.area_effective(wavelength)

    detected = lines_detected()

    # the emission is isotropic, so the radiance is the intensity spread over
    # the whole sphere
    radiance = detected.outputs / (4 * np.pi * u.sr)
    radiance = radiance.to(u.erg / u.s / u.cm**2 / u.sr)

    fig, ax = plt.subplots(
        figsize=(aastex.text_width_inches, 2.4),
        constrained_layout=True,
    )

    margin = 2 * u.AA
    ax.set_xlim(
        (wavelength_min - margin).to_value(u.AA),
        (wavelength_max + margin).to_value(u.AA),
    )
    ax.set_ylim(0, _headroom * na.value(radiance).max().ndarray)

    ax.set_xlabel(f"wavelength ({u.AA:latex_inline})")
    ax.set_ylabel(f"radiance ({na.unit(radiance):latex_inline})")

    ax_area = ax.twinx()
    ax_area.plot(
        wavelength.ndarray.to_value(u.AA),
        area.ndarray.value,
        color=_color_area,
    )

    # A twin is drawn after the axes it twins, so the curve would cover the
    # lines and their labels however low its own order. Drawing the lines'
    # axes last instead, with their background cleared so the curve shows
    # through, puts the curve beneath everything.
    ax.set_zorder(ax_area.get_zorder() + 1)
    ax.patch.set_visible(False)

    # The twin's frame no longer covers the labels either, so a label pushed
    # flush against the edge would break the frame with the padding of its
    # box. The frame is drawn over the labels instead.
    for spine in ax.spines.values():
        spine.set_zorder(matplotlib.text.Text.zorder + 1)
    ax_area.set_ylim(bottom=0)
    ax_area.set_ylabel(
        f"effective area ({(u.cm**2):latex_inline})",
        color=_color_area,
    )
    ax_area.tick_params(axis="y", colors=_color_area)

    # The labels are pushed apart where they are drawn, in the coordinates of
    # the display, so the limits and the layout must be final before they
    # are: changed afterward, the labels move with the data and land on one
    # another and on the frame.
    fig.draw_without_rendering()

    # Each label starts at its line and runs to the right. Fe XIV 467.4 is
    # faint and only two angstroms from Ne VII 465.2, so a label centered on
    # it covers the line of Ne VII, and is pushed across it. Starting at the
    # line, the labels of neighbors stack above one another instead of side
    # by side, so they need more room above than beside.
    utu.spectrum.stem(
        spectrum=na.FunctionArray(inputs=detected.inputs, outputs=radiance),
        ax=ax,
        latex=True,
        headroom=_headroom,
        kwargs_text={"fontsize": 6, "ha": "left"},
        kwargs_adjust={"expand": (1.3, 2.0)},
    )

    result = aastex.FigureStar("fig:bunch", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
The \numEmissionLines\ emission lines which put the most light on the
detector of \ESISII, those whose radiance times the effective area is
greatest, and the effective area of a single channel beneath them.
The lines are computed from version \chiantiVersion\ of the CHIANTI atomic
database~\citep{Dere1997,DelZanna2021}, using the coronal abundances of
\chiantiAbundances~\citep{Dere2023}, which raise the photospheric abundances
of \citet{Asplund2021} for the elements of low first ionization potential,
the \AR\ \DEM\ file \chiantiDEM, and $n_e T = $\,\chiantiPressure."""))

    return result
