"""The spectrum of an active region, as this article computes it."""

import importlib.metadata
import pathlib

import astropy.units as u
import esis
import named_arrays as na
import numpy as np
import utu

__all__ = [
    "abundance",
    "area_effective",
    "dem",
    "emission_measure",
    "lines",
    "num_grid",
    "pressure",
    "seed",
    "version",
]

abundance = "sun_coronal_2021_chianti"
"""
The abundances of the elements in the corona, as CHIANTI recommends them
:cite:p:`Dere2023`.

These are the photospheric abundances of :cite:t:`Asplund2021`, with those of
the elements whose first ionization potential is 10 eV or less raised by a
factor of :math:`10^{0.5}`, the enhancement typical of active regions. Of the
elements whose lines are brightest in the passband, that raises magnesium,
silicon and iron against neon and sulfur.
"""

dem = "active_region.dem"
"""
The differential emission measure of an active region, from CHIANTI.

ESIS-II observes the moss of an active region, so its passband is judged
against the spectrum of one, as it was in the proposal for the flight.
"""

pressure = 3e15 * u.K / u.cm**3
"""
The pressure of the active region, which sets the density at each temperature.

This is the pressure the header of :attr:`dem` says the differential
emission measure was derived at.
"""

seed = 42
"""
The seed of the sampling which estimates the effective area.

The field and the pupil are sampled at a point drawn inside each of their
cells, which keeps the quadrature from aliasing against the edge of an
aperture, at the cost of a different answer on every call. Fixing the seed
fixes the figure.
"""

num_grid = 20
"""
How finely the field and the pupil are sampled, as cells along each axis.

The same as the article on ESIS-I, where twenty took the roughness of the
curve down by a factor of three from the default of twelve.
"""

_axis = "temperature"
"""The name of the axis along the temperatures of the plasma."""


def temperature() -> na.AbstractScalar:
    """The temperatures the spectrum is computed at."""
    return na.ScalarArray(
        ndarray=10 ** np.arange(4, 8.1, 0.1) * u.K,
        axes=(_axis,),
    )


def emission_measure() -> na.AbstractScalar:
    """
    How much plasma the active region has at each temperature.

    Read from the CHIANTI differential emission measure file and interpolated
    in the logarithm of both quantities, since both run over several decades
    and a straight line through them is a straight line in neither.
    """
    import fiasco

    t = temperature()

    path = pathlib.Path(fiasco.defaults["ascii_dbase_root"]) / "dem" / dem
    rows = []
    for line in path.read_text().splitlines():
        field = line.split()
        if not field or field[0].startswith("%"):
            continue
        if float(field[0]) == -1:
            break
        rows.append((float(field[0]), float(field[1])))
    log_t, log_dem = np.array(rows).T

    result = np.interp(
        x=np.log10(t.ndarray.to_value(u.K)),
        xp=log_t,
        fp=log_dem,
        left=-np.inf,
        right=-np.inf,
    )
    result = (10**result) / (u.cm**5 * u.K)

    # the measure of each bin is the differential measure across it, the grid
    # being even in the logarithm
    result = result * t.ndarray * np.log(10) * 0.1

    return na.ScalarArray(result, axes=(_axis,))


def version() -> str:
    """The version of the CHIANTI database these numbers were computed from."""
    import fiasco
    from fiasco.util import read_chianti_version

    return str(read_chianti_version(fiasco.defaults["ascii_dbase_root"]))


@esis.memory.cache
def _lines(
    wavelength_min: u.Quantity,
    wavelength_max: u.Quantity,
    abundance: str,
    dem: str,
    pressure: u.Quantity,
    chianti_version: str,
) -> na.FunctionArray:
    """
    Compute the lines, and remember them, since it takes several minutes.

    Everything after the wavelengths is an argument so that it is part of
    what the cache is keyed on, since the answer depends on all of it:
    :mod:`joblib` hashes the arguments and the source of this function, and
    not the values it reads from the rest of the module or from the disk.
    Were :attr:`abundance` read here rather than passed in, changing it would
    be answered with the lines computed from the old one.

    ``dem`` and ``chianti_version`` are not read here. :func:`emission_measure`
    reads the file the one names, and the other is whichever database is
    installed.
    """
    t = temperature()
    return utu.spectrum.lines(
        temperature=t,
        density=pressure / t,
        emission_measure=emission_measure(),
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
        abundance=abundance,
        axis_temperature=_axis,
    )


def lines(
    wavelength_min: u.Quantity,
    wavelength_max: u.Quantity,
) -> na.FunctionArray:
    """
    The emission lines of an active region in a range of wavelengths,
    brightest first.

    Parameters
    ----------
    wavelength_min
        The shortest wavelength to compute.
    wavelength_max
        The longest wavelength to compute.
    """
    return _lines(
        wavelength_min=wavelength_min,
        wavelength_max=wavelength_max,
        abundance=abundance,
        dem=dem,
        pressure=pressure,
        chianti_version=version(),
    )


@esis.memory.cache
def _area_effective(
    wavelength: u.Quantity,
    num_grid: int,
    seed: int,
    optika_version: str,
    esis_version: str,
) -> na.AbstractScalar:
    """
    Trace the rays, and remember where they landed.

    ``optika_version`` and ``esis_version`` are not read here. They are
    arguments so that they are part of what the cache is keyed on, since the
    answer depends on which version traced the rays and on the design of
    ESIS-II, which is still changing, and nothing else in the key does.
    """
    optics = esis.flights.f2.optics.design_single(num_distribution=0)

    # The apertures are opened so that the curve is the response of the
    # coatings and the filter, rather than a map of where the light happens
    # to land.
    optics.filter.radius_clear = 1000 * u.mm
    optics.camera.sensor.num_pixel_x = 2 * optics.camera.sensor.num_pixel_x
    optics.camera.sensor.num_pixel_y = 2 * optics.camera.sensor.num_pixel_y

    def vertices(name: str) -> na.Cartesian2dVectorLinearSpace:
        return na.Cartesian2dVectorLinearSpace(
            start=-1,
            stop=1,
            axis=na.Cartesian2dVectorArray(f"{name}_x", f"{name}_y"),
            num=num_grid,
        )

    model = optics.system.area_effective(
        wavelength=wavelength,
        field=vertices("field"),
        pupil=vertices("pupil"),
        seed_field=seed,
        seed_pupil=seed,
    )

    return model(wavelength).to(u.cm**2)


def area_effective(wavelength: u.Quantity) -> na.AbstractScalar:
    """
    The effective area of one channel of ESIS-II, at each of ``wavelength``.

    Computed once and remembered, as the lines are, since tracing the rays
    is not something to pay for on every rebuild of the article.

    Parameters
    ----------
    wavelength
        The wavelengths to compute the effective area at.
    """
    return _area_effective(
        wavelength=wavelength,
        num_grid=num_grid,
        seed=seed,
        optika_version=importlib.metadata.version("optika"),
        esis_version=importlib.metadata.version("euv-snapshot-imaging-spectrograph"),
    )
