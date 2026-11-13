"""A simulated ESIS-II exposure of a MURaM simulation of an active region."""

import aastex
import astropy.units as u
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np

import esis2_science_paper

__all__ = [
    "fraction_masked",
    "muram",
]

_height = 6.2
"""
The height of the figure in inches.

It spans the width of the page, with a row of four maps of the scene above
the exposure. The detector is twice as wide as it is tall.
"""

fraction_masked = 0.2
"""
The fraction of the pixels of each map of the radiance, the faintest, whose
Doppler centroid is not drawn.
"""

_velocity_max = 40 * u.km / u.s
"""The largest Doppler centroid the color scale distinguishes."""


def muram() -> aastex.FigureStar:
    """
    A simulated exposure from one channel of ESIS-II of a MURaM simulation of
    an active region, below the radiance and Doppler centroid of
    \\NeVII and \\SiXII in the scene.
    """
    image = esis2_science_paper._muram.image_muram()
    radiance = esis2_science_paper._muram.radiance_muram()
    centroid = esis2_science_paper._muram.centroid_muram()

    position = radiance.inputs
    x = position.x.ndarray.to_value(u.arcsec)
    y = position.y.ndarray.to_value(u.arcsec)
    extent = (x.min(), x.max(), y.min(), y.max())

    axes_scene = ("scene_y", "scene_x")
    axes_detector = ("detector_y", "detector_x")
    unit_radiance = u.erg / u.cm**2 / u.s / u.sr

    fig = plt.figure(
        figsize=(aastex.text_width_inches, _height),
        layout="constrained",
    )
    fig_scene, fig_image = fig.subfigures(nrows=2, height_ratios=[1, 1.45])

    axs = fig_scene.subplots(ncols=4, sharex=True, sharey=True)
    names = [r"Ne\,\textsc{vii}", r"Si\,\textsc{xii}"]
    for j, name in enumerate(names):
        r = radiance.outputs[{"target": j}]
        r = r.to(unit_radiance).value.ndarray_aligned(axes_scene)
        c = centroid.outputs[{"target": j}]
        c = c.to(u.km / u.s).value.ndarray_aligned(axes_scene)
        c = np.ma.masked_where(r < np.quantile(r, fraction_masked), c)

        mappable = axs[j].imshow(
            r,
            norm=matplotlib.colors.PowerNorm(
                gamma=1 / 2,
                vmin=0,
                vmax=np.quantile(r, 0.997),
            ),
            origin="lower",
            extent=extent,
            cmap="afmhot",
            interpolation="none",
        )
        colorbar = fig_scene.colorbar(
            mappable,
            ax=axs[j],
            location="bottom",
            fraction=0.06,
            pad=0.02,
        )
        colorbar.set_label(f"radiance ({unit_radiance:latex_inline})", fontsize=7)
        colorbar.ax.tick_params(labelsize=7)
        colorbar.locator = matplotlib.ticker.MaxNLocator(nbins=4)
        colorbar.update_ticks()
        axs[j].set_title(f"{name} radiance", fontsize=8)

        cmap = matplotlib.colormaps["RdBu_r"].with_extremes(bad="0.75")
        mappable = axs[j + 2].imshow(
            c,
            vmin=-_velocity_max.value,
            vmax=_velocity_max.value,
            origin="lower",
            extent=extent,
            cmap=cmap,
            interpolation="none",
        )
        colorbar = fig_scene.colorbar(
            mappable,
            ax=axs[j + 2],
            location="bottom",
            fraction=0.06,
            pad=0.02,
        )
        colorbar.set_label(f"centroid ({u.km / u.s:latex_inline})", fontsize=7)
        colorbar.ax.tick_params(labelsize=7)
        colorbar.locator = matplotlib.ticker.MaxNLocator(nbins=4)
        colorbar.update_ticks()
        axs[j + 2].set_title(f"{name} Doppler centroid", fontsize=8)

    for ax in axs:
        ax.tick_params(labelsize=7)
        ax.set_xlabel(f"$x$ ({u.arcsec:latex_inline})", fontsize=7)
    axs[0].set_ylabel(f"$y$ ({u.arcsec:latex_inline})", fontsize=7)

    # Every pixel of the detector is drawn, rather than resampled to the
    # resolution of the figure. The read noise makes the darkest pixels
    # negative, which the norm draws as zero.
    electrons = image.outputs.to(u.electron).value.ndarray_aligned(axes_detector)
    ax = fig_image.subplots()
    mappable = ax.imshow(
        electrons,
        norm=matplotlib.colors.PowerNorm(gamma=1 / 2, vmin=0),
        origin="lower",
        cmap="afmhot",
        interpolation="none",
    )
    ax.set_xlabel(f"detector $x$ ({u.pix:latex_inline})")
    ax.set_ylabel(f"detector $y$ ({u.pix:latex_inline})")
    colorbar = fig_image.colorbar(mappable, ax=ax, fraction=0.03, pad=0.01)
    colorbar.set_label(f"signal ({u.electron:latex_inline})")

    result = aastex.FigureStar("fig:muram", position="!htb")
    result.add_fig(fig, width=None)

    return result
