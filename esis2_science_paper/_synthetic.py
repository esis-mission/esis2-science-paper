"""A simulated image from one channel of ESIS-II."""

import importlib.metadata

import astropy.units as u
import esis
import named_arrays as na

import esis2_science_paper

__all__ = [
    "fraction_min",
    "image_synthetic",
    "scene_synthetic",
    "wavelength_synthetic",
]

fraction_min = 0.005
"""
The least fraction of the radiance of the passband a line must carry to be in
the scene.
"""

_axis_x = "scene_x"
_axis_y = "scene_y"
"""
The names of the axes of the pixels of the scene, which are not those of the
detector it is imaged onto, so that the two cannot be confused.
"""

_packages = [
    "euv-snapshot-imaging-spectrograph",
    "msfc-ccd",
    "optika",
    "named-arrays",
    "utu",
    "solar-dynamics-observatory",
    "fiasco",
]
"""The packages the simulated image is computed with."""


def scene_synthetic() -> na.FunctionArray:
    """
    The scene ESIS-II is simulated observing.

    The default scene of :func:`esis.flights.f2.data.synth.scene_dem`: the
    active regions NOAA 12565 and 12567 on 2016 July 15, from the differential
    emission measure of the AIA images, in a square 500 arcseconds across.
    """
    return esis.flights.f2.data.synth.scene_dem(
        fraction_min=fraction_min,
        axis_detector_x=_axis_x,
        axis_detector_y=_axis_y,
    )


@esis.memory.cache
def _synthetic(
    fraction_min: float,
    versions: dict[str, str],
) -> tuple[na.FunctionArray, na.AbstractScalar]:
    """
    Compute and remember the simulated exposure and the lines it is made of.

    It takes minutes, mostly imaging the lines one by one.

    ``fraction_min`` and ``versions`` are not read here, but are part of the
    key the cache is looked up by: the first decides which lines are in the
    scene, and the second holds the versions of the packages and of the
    CHIANTI database the image is computed with.
    """
    scene = scene_synthetic()

    instrument = esis.flights.f2.optics.design_single(num_distribution=0)

    # One linear approximation of the instrument across the whole passband,
    # sampled about every angstrom. A cubic distortion puts every line within
    # a few hundredths of a pixel of where a fit to that line alone puts it.
    linear = instrument.system.linearize(
        wavelength=na.linspace(
            start=instrument.wavelength_min,
            stop=instrument.wavelength_max,
            axis="_wavelength",
            num=105,
        ),
        degree=2,
        degree_distortion=3,
    )

    rest = scene.inputs.wavelength_rest

    # The lines are imaged one at a time, since the regridding weights take
    # a few gigabytes per line, too many for all of them at once. Each is
    # exposed with its own shot noise but not integrated over wavelength,
    # which would add the read noise once per line rather than once for the
    # single readout of the sensor.
    electrons = 0
    for i in range(rest.shape["line"]):
        image = linear.image(
            scene=scene[{"line": i}],
            axis_wavelength="velocity",
            axis_field=(_axis_x, _axis_y),
            integrate=False,
        )
        electrons = electrons + image.outputs.sum("velocity")

    # the single readout of the sensor
    electrons = na.random.normal(loc=electrons, scale=linear.sensor.read_noise)

    result = na.FunctionArray(
        inputs=image.inputs.position,
        outputs=electrons.to(u.electron),
    )

    return result, rest


def image_synthetic() -> na.FunctionArray:
    """
    A simulated exposure from one channel of ESIS-II.

    The scene of :func:`scene_synthetic` imaged through a linear
    approximation of :func:`esis.flights.f2.optics.design_single`, line by
    line, onto its sensor for one exposure of its camera. The result is the
    electrons each pixel collects, with the shot noise of every line and the
    read noise of the readout.
    """
    image, _ = _cached()
    return image


def wavelength_synthetic() -> na.AbstractScalar:
    """The rest wavelength of each line of the simulated image."""
    _, wavelength = _cached()
    return wavelength


def _cached() -> tuple[na.FunctionArray, na.AbstractScalar]:
    """The result of :func:`_synthetic`, from the cache if it is there."""
    versions = {p: importlib.metadata.version(p) for p in _packages}
    versions["chianti"] = esis2_science_paper._spectrum.version()
    return _synthetic(
        fraction_min=fraction_min,
        versions=versions,
    )
