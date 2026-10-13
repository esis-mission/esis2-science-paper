import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import utu

import esis2_science_paper

__all__ = [
    "bunch",
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


def bunch() -> aastex.FigureStar:
    r"""
    The brightest lines in the passband, and the effective area beneath them.

    The lines are computed from the CHIANTI atomic database for an active
    region, and the effective area from the instrument model with the
    apertures of the filter and the sensor opened, so that the curve is the
    response of the coatings and the filter rather than a map of where the
    light happens to land.
    """
    optics = esis.flights.f2.optics.design_single(num_distribution=0)

    wavelength_min = optics.wavelength_min.to(u.AA).ndarray
    wavelength_max = optics.wavelength_max.to(u.AA).ndarray

    wavelength = na.linspace(
        start=wavelength_min,
        stop=wavelength_max,
        axis="wavelength",
        num=_num_wavelength,
    )

    area = esis2_science_paper._spectrum.area_effective(wavelength)

    lines = esis2_science_paper.lines(
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
    )

    brightest = lines[{"line": slice(num_emission_lines)}]

    # the emission is isotropic, so the radiance is the intensity spread over
    # the whole sphere
    radiance = brightest.outputs / (4 * np.pi * u.sr)
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
        zorder=0,
    )
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

    utu.spectrum.stem(
        spectrum=na.FunctionArray(inputs=brightest.inputs, outputs=radiance),
        ax=ax,
        latex=True,
        headroom=_headroom,
        kwargs_text={"fontsize": 6},
    )

    result = aastex.FigureStar("fig:bunch", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=aastex.NoEscape(r"\textwidth"))
    result.add_caption(aastex.NoEscape(r"""
The \numEmissionLines\ brightest emission lines in the \ESISII\ passband, and
the effective area of a single channel beneath them.
The lines are computed from version \chiantiVersion\ of the CHIANTI atomic
database~\citep{Dere1997,DelZanna2021}, using the coronal abundances of
\chiantiAbundances~\citep{Dere2023}, which raise the photospheric abundances
of \citet{Asplund2021} for the elements of low first ionization potential,
the \AR\ \DEM\ file \chiantiDEM, and $n_e T = $\,\chiantiPressure."""))

    return result
