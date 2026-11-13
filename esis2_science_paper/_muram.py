"""A simulated ESIS-II exposure of a MURaM simulation of an active region."""

import importlib.metadata
import os
import pathlib

import astropy.units as u
import esis
import joblib
import named_arrays as na
import numpy as np
import zarr

import esis2_science_paper

__all__ = [
    "centroid_muram",
    "image_muram",
    "radiance_muram",
    "stretch_muram",
    "wavelength_muram",
]

_velocity = na.linspace(-400, 300, axis="velocity", num=71) * u.km / u.s
"""
The vertices of the bins of line-of-sight velocity the lines of the scene are
spread over, those :func:`esis.flights.f2.data.synth.scene_muram` uses by
default.
"""

_num_chunk = 10
"""
The number of bins of velocity the scene is computed for at once.

The scene takes 4 bytes for each line in each bin in each of the million
pixels of the simulation, so it is computed a few bins at a time.
"""

_axis_x = "scene_x"
_axis_y = "scene_y"
"""
The names of the axes of the pixels of the scene, which are not those of the
detector it is imaged onto, so that the two cannot be confused.
"""

_axis_target = "target"
"""The name of the axis along the lines whose radiance is kept."""

_memory = joblib.Memory(
    location=pathlib.Path(__file__).parents[1] / "cache",
    mmap_mode="r",
    verbose=0,
)
"""
The cache of the simulated image, the directory ``cache`` at the root of the
repository, which is committed.

The image takes half an hour on a workstation and would take hours on a
runner of GitHub, which forgets a cache of its own after a week. So it is
computed on a workstation, and what :mod:`joblib` remembers of it is
committed beside the code which computed it.
"""

_packages = [
    "euv-snapshot-imaging-spectrograph",
    "msfc-ccd",
    "optika",
    "named-arrays",
    "utu",
    "fiasco",
]
"""The packages the simulated image is computed with."""


@_memory.cache
def _muram(
    fraction_min: float,
    velocity: u.Quantity,
    num_chunk: int,
    wavelength: u.Quantity,
    versions: dict[str, str],
) -> tuple[na.FunctionArray, na.FunctionArray, na.FunctionArray, na.AbstractScalar]:
    """
    Compute and remember the simulated exposure of the scene, the radiance
    and the Doppler centroid of the lines nearest `wavelength`, and the rest
    wavelength of every line of the scene.

    It takes tens of minutes, mostly imaging each line in each group of bins
    of velocity.

    The results are single precision, which halves what is committed and is
    far finer than the figure can show.

    ``versions`` is not read here, but is part of the key the cache is looked
    up by: it holds the versions of the packages and of the CHIANTI database
    the image is computed with.
    """
    velocity = na.ScalarArray(velocity, axes="velocity")
    wavelength = na.ScalarArray(wavelength, axes=_axis_target)

    instrument = esis.flights.f2.optics.design_single(num_distribution=0)

    # One linear approximation of the instrument across the whole passband,
    # as for the image of the scene from AIA.
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

    # The scene is computed for a group of bins of velocity at a time, and
    # each of its lines imaged one at a time, as for the image of the scene
    # from AIA. Each is exposed with its own shot noise but not integrated
    # over wavelength, so that the read noise is added once, for the single
    # readout of the sensor.
    axis_field = (_axis_x, _axis_y)
    num_bin = velocity.shape["velocity"] - 1
    electrons = 0
    radiance = 0
    moment = 0
    for k in range(0, num_bin, num_chunk):
        v = velocity[{"velocity": slice(k, k + num_chunk + 1)}]
        scene = esis.flights.f2.data.synth.scene_muram(
            velocity=v,
            fraction_min=fraction_min,
            axis_x=_axis_x,
            axis_y=_axis_y,
        )

        # the radiance of the lines nearest `wavelength`, and its first
        # moment in velocity
        rest = scene.inputs.wavelength_rest
        index = np.argmin(np.abs(rest - wavelength), axis="line")
        width = scene.inputs.wavelength.volume_cell("velocity")[index]
        spectrum = scene.outputs[index]
        center = v.cell_centers("velocity")
        radiance = radiance + na.vecdot(spectrum, width, axis="velocity")
        moment = moment + na.vecdot(spectrum, width * center, axis="velocity")

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

    # the single readout of the sensor
    electrons = na.random.normal(loc=electrons, scale=linear.sensor.read_noise)

    position = scene.inputs.position
    image = na.FunctionArray(
        inputs=image.inputs.position,
        outputs=electrons.to(u.electron).astype(np.float32),
    )
    centroid = na.FunctionArray(
        inputs=position,
        outputs=(moment / radiance).to(u.km / u.s).astype(np.float32),
    )
    radiance = na.FunctionArray(
        inputs=position,
        outputs=radiance.to(u.erg / u.cm**2 / u.s / u.sr).astype(np.float32),
    )

    return image, radiance, centroid, rest


def image_muram() -> na.FunctionArray:
    """
    A simulated exposure from one channel of ESIS-II of the scene of
    :func:`esis.flights.f2.data.synth.scene_muram`.

    The scene imaged through a linear approximation of
    :func:`esis.flights.f2.optics.design_single`, line by line, onto its sensor
    for one exposure of its camera. The result is the electrons each pixel
    collects, with the shot noise of every line and the read noise of the
    readout.
    """
    image, _, _, _ = _cached()
    return image


def radiance_muram() -> na.FunctionArray:
    """
    The radiance of Ne VII 465 and Si XII 499 in each pixel of the scene of
    :func:`image_muram`, along the axis ``"target"``, in that order.
    """
    _, radiance, _, _ = _cached()
    return radiance


def centroid_muram() -> na.FunctionArray:
    """
    The Doppler centroid of the lines of :func:`radiance_muram` in each pixel
    of the scene, positive away from the observer.
    """
    _, _, centroid, _ = _cached()
    return centroid


def wavelength_muram() -> na.AbstractScalar:
    """The rest wavelength of each line of the scene of :func:`image_muram`."""
    _, _, _, wavelength = _cached()
    return wavelength


def stretch_muram() -> float:
    """
    How many times its true size the simulation is drawn in the scene.

    The angle each pixel of the scene spans, one pixel of the detector, over
    the angle a pixel of the simulation would span seen from one astronomical
    unit away.
    """
    version = importlib.metadata.version("euv-snapshot-imaging-spectrograph")
    true = (_width_pixel(version) / u.au).to(
        unit=u.arcsec,
        equivalencies=u.dimensionless_angles(),
    )
    x = radiance_muram().inputs.x
    scene = x[{_axis_x: 1}] - x[{_axis_x: 0}]
    return float((scene.ndarray / true).to_value(u.dimensionless_unscaled))


@_memory.cache
def _width_pixel(version: str) -> u.Quantity:
    """
    Read and remember the width of a pixel of the simulation.

    Remembered beside the image, so that only the computer which computes
    the image downloads the simulation.

    ``version`` is not read here, but is part of the key the cache is looked
    up by: it is the version of ``esis``, which names the simulation.
    """
    store = zarr.open_group(esis.flights.f2.data.synth.path_muram(), mode="r")
    x = store["x"][:] * u.cm
    return x[1] - x[0]


def _cached() -> tuple[
    na.FunctionArray,
    na.FunctionArray,
    na.FunctionArray,
    na.AbstractScalar,
]:
    """
    The result of :func:`_muram`, from the cache if it is there.

    A runner of GitHub does not compute it, which would take hours, and
    fails instead.
    """
    versions = {p: importlib.metadata.version(p) for p in _packages}
    versions["chianti"] = esis2_science_paper._spectrum.version()
    wavelength = u.Quantity(
        [
            esis2_science_paper._spectrum.wavelength_ne_vii,
            esis2_science_paper._spectrum.wavelength_si_xii,
        ]
    )
    kwargs = {
        "fraction_min": esis2_science_paper._synthetic.fraction_min,
        "velocity": _velocity.explicit.ndarray,
        "num_chunk": _num_chunk,
        "wavelength": wavelength,
        "versions": versions,
    }
    if os.environ.get("CI") and not _muram.check_call_in_cache(**kwargs):
        raise RuntimeError(
            "The simulated image of the MURaM simulation in `cache` was "
            f"computed with other versions of the packages than {versions}, "
            "or by other code. It takes hours to compute here, so compute it "
            "on a workstation with `esis2_science_paper.image_muram()`, and "
            "commit the new directory in `cache` in place of the old one."
        )
    return _muram(**kwargs)
