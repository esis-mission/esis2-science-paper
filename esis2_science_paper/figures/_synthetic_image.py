"""A simulated image from one channel of ESIS-II."""

import aastex
import astropy.units as u
import matplotlib.colors
import matplotlib.pyplot as plt

import esis2_science_paper

__all__ = [
    "synthetic_image",
]

_height = 3.6
"""
The height of the figure in inches.

It spans the width of the page, and the detector is twice as wide as it is
tall, which leaves room beside it for the color bar.
"""


def synthetic_image() -> aastex.FigureStar:
    """
    A simulated exposure from one channel of ESIS-II, on a square-root scale.

    The electrons each pixel of the detector collects in one exposure, with
    noise, from the scene of
    :func:`esis2_science_paper._synthetic.scene_synthetic`.
    """
    image = esis2_science_paper._synthetic.image_synthetic()

    electrons = image.outputs.to(u.electron).value
    electrons = electrons.ndarray_aligned(("detector_y", "detector_x"))

    fig, ax = plt.subplots(
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
    ax.set_xlabel(f"detector $x$ ({u.pix:latex_inline})")
    ax.set_ylabel(f"detector $y$ ({u.pix:latex_inline})")

    colorbar = fig.colorbar(mappable, ax=ax, fraction=0.03, pad=0.01)
    colorbar.set_label(f"signal ({u.electron:latex_inline})")

    result = aastex.FigureStar("fig:synthetic", position="!htb")
    result.add_fig(fig, width=None)
    result.add_caption(aastex.NoEscape(r"""
A simulated \timeExposure\ exposure from one channel of \ESISII, in the electrons
collected by each pixel of the \CCD, on a square-root scale, with the shot noise of
the photons and the read noise of the camera.
The scene is the active regions NOAA 12565 and 12567 at 00:00~UT on 2016 July 15:
the \DEM\ of each \AIA\ pixel, inverted from the six optically thin \EUV\ channels
with the method of \citet{Plowman2020}, and the \numLinesScene\ lines of the
passband which carry at least \fractionLineMin\ of its radiance, at rest.
The images of \NeVII\ and \SiXII\ fall on either side of the center, the weaker
\SiXII\ line clips the right edge, and lines of \MgVII\ and \MgVIII\ clip the
left."""))

    return result
