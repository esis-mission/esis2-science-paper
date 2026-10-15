"""A simulated image from one channel of ESIS-II."""

import importlib.metadata

import astropy.units as u
import esis
import named_arrays as na
import optika

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
    Compute and remember the simulated image and the lines it is made of.

    It takes minutes, mostly imaging the lines one by one.

    ``fraction_min`` and ``versions`` are not read here, but are part of the
    key the cache is looked up by: the first decides which lines are in the
    scene, and the second holds the versions of the packages and of the
    CHIANTI database the image is computed with.
    """
    scene = scene_synthetic()

    instrument = esis.flights.f2.optics.design_single(num_distribution=0)
    system = instrument.system
    system.sensor.material = optika.sensors.materials.IdealSensorMaterial()
    system.sensor.timedelta_exposure = 1 * u.s

    rest = scene.inputs.wavelength_rest

    rate = 0
    for i in range(rest.shape["line"]):
        index = {"line": i}
        w = rest[index]

        # The fits of the linear system are polynomials in wavelength, so
        # each line is linearized on its own, over a couple of angstroms.
        linear = system.linearize(
            wavelength=na.linspace(w - 1 * u.AA, w + 1 * u.AA, axis="_w", num=5),
            degree=2,
        )

        image = linear.image(
            scene=scene[index],
            axis_wavelength="velocity",
            axis_field=(_axis_x, _axis_y),
            noise=False,
        )

        rate = rate + image.outputs / system.sensor.timedelta_exposure

    result = na.FunctionArray(
        inputs=image.inputs,
        outputs=rate.to(u.electron / u.s),
    )

    return result, rest


def image_synthetic() -> na.FunctionArray:
    """
    A simulated image from one channel of ESIS-II.

    The scene of :func:`scene_synthetic` imaged through a linear
    approximation of :func:`esis.flights.f2.optics.design_single`, line by
    line, with no noise. The sensor is ideal, counting one electron for
    every photon which reaches it, so the result is the rate at which
    photons arrive at each pixel.
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
