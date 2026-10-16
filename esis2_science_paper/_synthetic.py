"""A simulated image from one channel of ESIS-II."""

import importlib.metadata

import astropy.units as u
import esis
import named_arrays as na
import numpy as np

import esis2_science_paper

__all__ = [
    "fraction_min",
    "image_synthetic",
    "scene_synthetic",
    "size_block",
    "snr_synthetic",
    "wavelength_synthetic",
]

fraction_min = 0.005
"""
The least fraction of the radiance of the passband a line must carry to be in
the scene.
"""

size_block = 2
"""
The number of pixels along each side of a resolution element, a block of
pixels which the signal-to-noise ratio is computed for.

Two pixels sample the finest detail the detector can resolve.
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
) -> tuple[na.FunctionArray, na.FunctionArray, na.AbstractScalar]:
    """
    Compute and remember the simulated exposure, its signal-to-noise ratio,
    and the lines it is made of.

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
    # single readout of the sensor. The same weights expose each line again
    # without noise, for the electrons each pixel collects on average.
    axis_field = (_axis_x, _axis_y)
    sensor = linear.sensor
    electrons = 0
    signal = 0
    variance = 0
    for i in range(rest.shape["line"]):
        line = scene[{"line": i}].explicit
        weights = linear.weights(
            coordinates=line.inputs,
            axis_wavelength="velocity",
            axis_field=axis_field,
        )
        image = linear.image_from_weights(
            weights,
            line,
            axis_wavelength="velocity",
            axis_field=axis_field,
            integrate=False,
        )
        electrons = electrons + image.outputs.sum("velocity")
        expected = linear.image_from_weights(
            weights,
            line,
            axis_wavelength="velocity",
            axis_field=axis_field,
            integrate=False,
            noise=False,
        )
        signal = signal + expected.outputs.sum("velocity")

        # The shot noise of the photons each pixel absorbs, and the spread
        # of the charge each frees, without the charge diffusion of the
        # sensor (a pixel width of zero). Diffusion lowers the noise of each
        # pixel by sharing the charge of a photon with its neighbors, which
        # correlates their noise rather than removing it, so the variances of
        # neighboring pixels could not be added if it were included.
        noise_shot = sensor.material.uncertainty(
            electrons=expected.outputs,
            wavelength=expected.inputs.wavelength.cell_centers("velocity"),
            direction=linear.direction,
            width_pixel=0 * u.um,
        )
        variance = variance + np.square(noise_shot).sum("velocity")

    # the single readout of the sensor
    electrons = na.random.normal(loc=electrons, scale=sensor.read_noise)

    # The signal-to-noise ratio of each resolution element: the electrons
    # its pixels collect on average, over the noise of their sum, with the
    # read noise of each of its pixels.
    def block(a: na.AbstractScalar) -> na.AbstractScalar:
        """The sum of each resolution element of an image of the sensor."""
        for axis in (sensor.axis_pixel.x, sensor.axis_pixel.y):
            parts = [a[{axis: slice(i, None, size_block)}] for i in range(size_block)]
            a = na.stack(parts, axis="_block").sum("_block")
        return a

    noise_read = sensor.read_noise * size_block
    snr = block(signal) / np.sqrt(block(variance) + np.square(noise_read))

    position = image.inputs.position
    result = na.FunctionArray(
        inputs=position,
        outputs=electrons.to(u.electron),
    )
    snr = na.FunctionArray(
        inputs=position[
            {
                sensor.axis_pixel.x: slice(None, None, size_block),
                sensor.axis_pixel.y: slice(None, None, size_block),
            }
        ],
        outputs=snr.to(u.dimensionless_unscaled),
    )

    return result, snr, rest


def image_synthetic() -> na.FunctionArray:
    """
    A simulated exposure from one channel of ESIS-II.

    The scene of :func:`scene_synthetic` imaged through a linear
    approximation of :func:`esis.flights.f2.optics.design_single`, line by
    line, onto its sensor for one exposure of its camera. The result is the
    electrons each pixel collects, with the shot noise of every line and the
    read noise of the readout.
    """
    image, _, _ = _cached()
    return image


def snr_synthetic() -> na.FunctionArray:
    """
    The signal-to-noise ratio of each resolution element of
    :func:`image_synthetic`, a block of :data:`size_block` pixels on a side.

    The electrons its pixels collect on average, over the standard deviation
    of the noise of their sum: the shot noise of every line, from the photons
    the sensor absorbs and the spread of the charge each frees, and the read
    noise of each of its pixels. The charge diffusion of the sensor is left
    out, since it lowers the noise of each pixel only by correlating it with
    its neighbors.
    """
    _, snr, _ = _cached()
    return snr


def wavelength_synthetic() -> na.AbstractScalar:
    """The rest wavelength of each line of the simulated image."""
    _, _, wavelength = _cached()
    return wavelength


def _cached() -> tuple[na.FunctionArray, na.FunctionArray, na.AbstractScalar]:
    """The result of :func:`_synthetic`, from the cache if it is there."""
    versions = {p: importlib.metadata.version(p) for p in _packages}
    versions["chianti"] = esis2_science_paper._spectrum.version()
    return _synthetic(
        fraction_min=fraction_min,
        versions=versions,
    )
