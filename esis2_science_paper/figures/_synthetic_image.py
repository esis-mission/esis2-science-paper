"""A simulated image from one channel of ESIS-II."""

import aastex
import astropy.units as u
import matplotlib.colors
import matplotlib.pyplot as plt
import matplotlib.ticker

import esis2_science_paper

__all__ = [
    "synthetic_image",
]

_height = 6.2
"""
The height of the figure in inches.

It spans the width of the page, with the exposure above its signal-to-noise
ratio. The detector is twice as wide as it is tall, which leaves room beside
each for its color bar.
"""


def synthetic_image() -> aastex.FigureStar:
    """
    A simulated exposure from one channel of ESIS-II, and its signal-to-noise
    ratio.

    Above, the electrons each pixel of the detector collects in one exposure,
    with noise, from the scene of
    :func:`esis2_science_paper._synthetic.scene_synthetic`, on a square-root
    scale. Below, the signal-to-noise ratio of each resolution element, a
    block of :data:`esis2_science_paper._synthetic.size_block` pixels on a
    side.
    """
    image = esis2_science_paper._synthetic.image_synthetic()
    snr = esis2_science_paper._synthetic.snr_synthetic()

    axes = ("detector_y", "detector_x")
    electrons = image.outputs.to(u.electron).value.ndarray_aligned(axes)
    snr = snr.outputs.to(u.dimensionless_unscaled).value.ndarray_aligned(axes)

    fig, (ax, ax_snr) = plt.subplots(
        nrows=2,
        sharex=True,
        sharey=True,
        figsize=(aastex.text_width_inches, _height),
        constrained_layout=True,
    )

    # Every pixel of the detector is drawn, rather than resampled to the
    # resolution of the figure.
    # The read noise makes the darkest pixels negative, which the norm
    # draws as zero.
    mappable = ax.imshow(
        electrons,
        norm=matplotlib.colors.PowerNorm(gamma=1 / 2, vmin=0),
        origin="lower",
        cmap="afmhot",
        interpolation="none",
    )
    ax.set_ylabel(f"detector $y$ ({u.pix:latex_inline})")

    colorbar = fig.colorbar(mappable, ax=ax, fraction=0.03, pad=0.01)
    colorbar.set_label(f"signal ({u.electron:latex_inline})")

    # Each resolution element covers its block of pixels, so that the two
    # rows line up.
    # The signal-to-noise ratio spans decades, so it is drawn on a
    # logarithmic scale, and anything below one is drawn as one, including
    # the elements no light reaches, whose ratio of zero has no logarithm.
    num_y, num_x = electrons.shape
    cmap = matplotlib.colormaps["viridis"]
    mappable = ax_snr.imshow(
        snr,
        norm=matplotlib.colors.LogNorm(vmin=1),
        origin="lower",
        extent=(-0.5, num_x - 0.5, -0.5, num_y - 0.5),
        cmap=cmap.with_extremes(under=cmap(0), bad=cmap(0)),
        interpolation="none",
    )
    ax_snr.set_xlabel(f"detector $x$ ({u.pix:latex_inline})")
    ax_snr.set_ylabel(f"detector $y$ ({u.pix:latex_inline})")

    colorbar = fig.colorbar(mappable, ax=ax_snr, fraction=0.03, pad=0.01)
    colorbar.set_ticks([1, 2, 5, 10, 20])
    colorbar.ax.yaxis.set_major_formatter(matplotlib.ticker.ScalarFormatter())
    colorbar.ax.yaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    colorbar.set_label("signal-to-noise ratio")

    result = aastex.FigureStar("fig:synthetic", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
Above, a simulated \timeExposure\ exposure from one channel of \ESISII, in the
electrons collected by each pixel of the \CCD, on a square-root scale, with the shot
noise of the photons and the read noise of the camera.
The scene is the active regions NOAA 12565 and 12567 at 00:00~UT on 2016 July 15:
the \DEM\ of each \AIA\ pixel, inverted from the six optically thin \EUV\ channels
with the method of \citet{Plowman2020}, and the \numLinesScene\ lines of the
passband which carry at least \fractionLineMin\ of its radiance, at rest.
The images of \NeVII\ and \SiXII\ fall on either side of the center, the weaker
\SiXII\ line clips the right edge, and lines of \MgVII\ and \MgVIII\ clip the
left.
Below, on a logarithmic scale, the \SNR\ of each resolution element, a block of
$\sizeBlock \times \sizeBlock$ pixels: the electrons it collects on average, over the
standard deviation of the noise of their sum, from the shot noise of the photons it
absorbs, the spread of the charge each frees, and the read noise of each of its
pixels.
It leaves out the charge which diffuses between pixels, which lowers the noise of
each pixel only by correlating it with its neighbors."""))

    return result
