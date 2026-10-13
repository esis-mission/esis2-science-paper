import aastex
import astropy.units as u
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import utu

import esis2_science_paper

__all__ = [
    "contribution",
]

_decades = 3
"""How many decades below the highest peak the axes reach."""


def contribution() -> aastex.Figure:
    r"""
    The contribution functions of the two lines ESIS-II observes, and of the
    line of Si IV in which Testa et al. (2014) saw the upflows of beam heating.

    The line of Si IV is drawn dashed and in gray, since ESIS-II does not
    observe it. It is there to show how much hotter Ne VII is formed.
    """
    spectrum = esis2_science_paper._spectrum

    lines = [
        ("Ne 7", spectrum.wavelength_ne_vii, {"color": "tab:blue"}),
        ("Si 12", spectrum.wavelength_si_xii, {"color": "tab:orange"}),
        ("Si 4", spectrum.wavelength_si_iv, {"color": "gray", "linestyle": "dashed"}),
    ]

    fig, ax = plt.subplots(
        figsize=(aastex.column_width_inches, 2.2),
        constrained_layout=True,
    )

    functions = [spectrum.contribution_function(ion, w) for ion, w, _ in lines]
    unit = functions[0].outputs.unit

    peak = 0
    for (ion, wavelength, kwargs), g in zip(lines, functions):
        t = g.inputs.ndarray.to_value(u.MK)
        y = g.outputs.ndarray.to_value(unit)

        ax.plot(t, y, **kwargs)

        i = np.argmax(y)
        name = utu.spectrum.spectroscopic(ion, latex=True)
        ax.text(
            x=t[i],
            y=1.3 * y[i],
            s=rf"{name} {wavelength.to_value(u.AA):.1f}\,\AA",
            ha="center",
            va="bottom",
            fontsize=7,
        )
        peak = max(peak, y[i])

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlim(0.03, 10)
    ax.set_ylim(peak / 10**_decades, 5 * peak)

    # the temperatures are a few hundredths of a megakelvin to a few, and
    # read more easily as decimals than as powers of ten
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:g}"))

    ax.set_xlabel(f"temperature ({u.MK:latex_inline})")
    ax.set_ylabel(f"$G(T)$ ({unit:latex_inline})")

    result = aastex.Figure("fig:contribution", position="!htb")
    result.append(aastex.NoEscape(r"\centering"))
    result.add_fig(fig, width=aastex.NoEscape(r"\columnwidth"))
    result.add_caption(aastex.NoEscape(r"""
The contribution functions of the two lines \ESISII\ observes (solid), and of
the \SiIV\ line in which \citet{Testa2014} saw the upflows of beam heating
with \IRIS\ (dashed).
Each is the emissivity of the line per steradian divided by $n_e n_H$,
computed from version \chiantiVersion\ of the CHIANTI atomic
database~\citep{Dere1997,DelZanna2021} with the abundances and the pressure
of Figure~\ref{fig:bunch}.
The peaks, at \temperatureSiIV, \temperatureNeVII, and \temperatureSiXII,
are the temperatures at which the lines are formed."""))

    return result
