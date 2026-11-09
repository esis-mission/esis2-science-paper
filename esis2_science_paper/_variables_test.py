import aastex
import astropy.units as u
import optika

import esis2_science_paper


def test_variables():
    result = esis2_science_paper.variables()
    assert result
    assert all(isinstance(v, aastex.Variable) for v in result)


def test_variables_unique():
    """A name defined twice would silently take whichever value came last."""
    names = [v.name for v in esis2_science_paper.variables()]
    assert len(names) == len(set(names))


def test_num_periods():
    """The top period, built apart from the rest, is counted with them."""
    Si = optika.materials.Layer(chemical="Si", thickness=13 * u.nm)
    Sc = optika.materials.Layer(chemical="Sc", thickness=13 * u.nm)
    multilayer = optika.materials.MultilayerMirror(
        layers=[
            Si,
            Sc,
            optika.materials.PeriodicLayerSequence([Si, Sc], num_periods=4),
        ],
        substrate=optika.materials.Layer(chemical="SiO2"),
    )
    assert esis2_science_paper._variables._num_periods(multilayer) == 5
