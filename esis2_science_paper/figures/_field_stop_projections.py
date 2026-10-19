"""Where the image of the field stop lands on the detector at each bright line."""

import aastex
import astropy.units as u
import esis
import matplotlib.pyplot as plt
import named_arrays as na
import numpy as np
import utu

import esis2_science_paper

__all__ = [
    "field_stop_projections",
]

_height = 2.85
"""
The height of the figure in inches, about the least which keeps the legend
clear of the label of the :math:`x` axis.

Its width is the width of a column, and the detector is twice as wide as it
is tall, which leaves room beneath it for the legend. The ESIS-I instrument
paper's 3 inches left a band empty above the plot.
"""

_colormap = "turbo"
"""
The colormap the lines are colored from, in order of wavelength.

It runs from violet to red, shortest wavelength first, as in the same figure
of the ESIS-I instrument paper.
"""


def field_stop_projections() -> aastex.Figure:
    """
    The image of the field stop on the detector of a single channel, at each
    of the lines which put the most light on it.

    The lines are the ones the passband figure labels, those of
    :func:`esis2_science_paper.figures.lines_detected`, so that the two
    figures name the same lines. The field stop is ahead of the grating, so its
    outline in field angles is the same at every wavelength, and the grating
    moves its image along the dispersion as the wavelength changes.
    """
    optics = esis.flights.f2.optics.design_single(num_distribution=0)
    system = optics.system
    sensor = system.sensor

    lines = esis2_science_paper.figures.lines_detected()
    num = lines.shape["line"]

    wavelength = lines.inputs.components["wavelength"]
    names = utu.spectrum.spectroscopic(
        ion=lines.inputs.components["ion"],
        latex=True,
    )

    # The outline of the field of view in field angles, carried onto the
    # detector by the chief ray through each of its points. The stop is at
    # the focus of the primary mirror, so every ray through a point on its
    # edge lands in the same place.
    outline = system.field_stop_polygon(wavelength).wire().xy
    rayfunction = system.rayfunction(
        wavelength=wavelength,
        field=outline,
        pupil=na.Cartesian2dVectorArray(0, 0),
        normalized_field=False,
    )
    image = sensor.pixels(rayfunction.outputs.position.xy)

    order = np.argsort(na.as_named_array(wavelength).ndarray.value)
    colors = plt.get_cmap(_colormap)(np.linspace(0, 1, num))

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, _height),
        constrained_layout=True,
    )

    for color, index in zip(colors, order):
        i = {"line": int(index)}
        w = na.as_named_array(wavelength[i]).ndarray.to_value(u.AA)
        ax.plot(
            image.x[i].ndarray.to_value(u.pix),
            image.y[i].ndarray.to_value(u.pix),
            color=color,
            label=rf"{names[i].ndarray} {w:.2f}\,\AA",
        )

    # the axes are the light-sensitive area of the detector
    num_pixel = sensor.num_pixel
    ax.set_xlim(0, num_pixel.x)
    ax.set_ylim(0, num_pixel.y)
    ax.set_aspect("equal")
    ax.set_xlabel(f"detector $x$ ({u.pix:latex_inline})")
    ax.set_ylabel(f"detector $y$ ({u.pix:latex_inline})")
    fig.legend(loc="outside lower center", ncol=2)

    result = aastex.Figure("fig:projections", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
The image of the field stop on the detector of a single \ESISII\ channel, at
each of the \numEmissionLines\ lines of Figure~\ref{fig:bunch}.
The axes span the active area of the \CCD."""))

    return result
