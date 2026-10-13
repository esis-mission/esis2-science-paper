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
    "contribution_function",
    "dem",
    "emission_measure",
    "lines",
    "num_grid",
    "pressure",
    "seed",
    "temperature_formation",
    "version",
    "wavelength_ne_vii",
    "wavelength_si_iv",
    "wavelength_si_xii",
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

wavelength_ne_vii = 465.221 * u.AA
"""The wavelength of the line of Ne VII which ESIS-II observes, as CHIANTI lists it."""

wavelength_si_xii = 499.406 * u.AA
"""The wavelength of the line of Si XII which ESIS-II observes, as CHIANTI lists it."""

wavelength_si_iv = 1402.770 * u.AA
"""
The wavelength of the line of Si IV in which :cite:t:`Testa2014` saw the
upflows of beam heating with IRIS, as CHIANTI lists it.
"""

_axis = "temperature"
"""The name of the axis along the temperatures of the plasma."""


def temperature() -> na.AbstractScalar:
    """The temperatures the spectrum is computed at."""
    return na.ScalarArray(
        ndarray=10 ** np.arange(4, 8.1, 0.1) * u.K,
        axes=(_axis,),
    )


_num_slice = 50
"""
How many temperatures the level populations of an ion are solved at at once.

Si XII, the largest of the ions, takes about a seventh of a gigabyte for
each, so this many takes about seven, under half of what a runner has.
Fewer slices are faster, since :mod:`fiasco` builds the ion each one
recombines from anew for every slice, and with it a ratio of protons to
electrons which takes tens of seconds.
"""


def _temperature_fine() -> na.AbstractScalar:
    """
    The temperatures the contribution functions are computed at.

    Five times finer than :func:`temperature`, which need only be as fine as
    the differential emission measure it is summed against. A tenth of a
    decade is half the width of the narrowest peak, so the curves would be
    drawn as a few straight lines, and finer than the twentieth of a decade
    CHIANTI tabulates its ionization fractions at, so they are drawn as
    :mod:`fiasco` interpolates between them.
    """
    return na.ScalarArray(
        ndarray=10 ** np.arange(4, 7.501, 0.02) * u.K,
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
def _contribution_function(
    ion: str,
    wavelength: u.Quantity,
    temperature: na.AbstractScalar,
    abundance: str,
    pressure: u.Quantity,
    chianti_version: str,
) -> na.FunctionArray:
    """
    Compute the contribution function of a line, and remember it, since it
    takes several minutes.

    Everything after the wavelength is an argument for the reason it is in
    :func:`_lines`, so that it is part of what the cache is keyed on. That
    includes the temperatures: computed here from :func:`_temperature_fine`,
    a change to the grid would be answered with the curves of the old one.
    """
    import fiasco

    t = temperature

    # The ratio of protons to electrons is the slow part of a small ion, and
    # depends on nothing but the temperature, so it is computed once rather
    # than once for each slice.
    ratio = na.ScalarArray(
        ndarray=fiasco.proton_electron_ratio(t.ndarray, abundance=abundance),
        axes=(_axis,),
    )

    # The level populations are solved at every temperature at once, in a
    # matrix as wide as the ion has levels. Si XII and the ion it recombines
    # from have over nine hundred between them, which at every temperature of
    # the grid is nearly fifty gigabytes, three times what a runner of the
    # continuous integration has. Each temperature is solved on its own, so
    # solving a slice of them at a time changes nothing but the memory.
    g = []
    for start in range(0, t.size, _num_slice):
        index = {_axis: slice(start, start + _num_slice)}
        t_slice = t[index]

        result = utu.spectrum.contribution_function(
            ion=fiasco.Ion(ion, t_slice.ndarray, abundance=abundance),
            density=pressure / t_slice,
            axis_temperature=_axis,
            proton_electron_ratio=ratio[index],
        )

        # An observed line is every transition at its wavelength, of which
        # there can be more than one, so all of them are summed. CHIANTI
        # lists its wavelengths to the milliangstrom, so that is how close
        # they must be.
        where = np.abs(result.inputs.ndarray - wavelength) < 0.5 * u.mAA
        if not np.any(where):
            raise ValueError(f"CHIANTI lists no line of {ion} at {wavelength}.")
        lines = na.ScalarArray(np.flatnonzero(where), axes="line")
        g.append(result.outputs[{"line": lines}].sum("line"))

    g = na.concatenate(g, axis=_axis)

    # the emission is isotropic, so the emissivity is spread over the whole
    # sphere, as the radiance of each line is
    return na.FunctionArray(
        inputs=t,
        outputs=(g / (4 * np.pi * u.sr)).to(u.erg * u.cm**3 / u.s / u.sr),
    )


def contribution_function(
    ion: str,
    wavelength: u.Quantity,
) -> na.FunctionArray:
    """
    The contribution function of a line, as a function of temperature.

    This is the emissivity of the line per steradian, divided by the number
    densities of the electrons and of hydrogen, computed with the abundances
    and the pressure of the spectrum of :func:`lines`.

    Parameters
    ----------
    ion
        The ion which emits the line, as :mod:`fiasco` names it, ``"Ne 7"``
        for instance.
    wavelength
        The wavelength of the line, as CHIANTI lists it.
    """
    return _contribution_function(
        ion=ion,
        wavelength=wavelength,
        temperature=_temperature_fine(),
        abundance=abundance,
        pressure=pressure,
        chianti_version=version(),
    )


def temperature_formation(
    ion: str,
    wavelength: u.Quantity,
) -> u.Quantity:
    """
    The temperature at which a line is formed, where its contribution
    function peaks.

    Parameters
    ----------
    ion
        The ion which emits the line, as :mod:`fiasco` names it.
    wavelength
        The wavelength of the line, as CHIANTI lists it.
    """
    g = contribution_function(ion, wavelength)
    return g.inputs[np.argmax(g.outputs, axis=_axis)].ndarray


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
