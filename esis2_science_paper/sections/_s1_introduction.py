import aastex

__all__ = [
    "introduction",
]


def introduction() -> aastex.Section:
    result = aastex.Section("Introduction")
    result.append(r"""
\begin{outline}
\item \textbf{Coronal heating by nanoflares.}
    Energy stored in the braided coronal field is released by many small reconnection
    events~\citep{Parker1988}.
    As in flares, much of it may go into nonthermal electrons which stream down the field and heat
    the \TR\ and chromosphere~\citep{Emslie1978}, and such beams arise in simulations of
    nanoflares~\citep{Bakke2018}, so heating by electron beams is a signature of reconnection.
\item \textbf{The observational gap.}
    Beam heating shows up as brightenings and blue shifts in \TR\ lines at the footpoints of hot
    loops, lasting tens of seconds~\citep{Testa2014}.
    Velocities are measured by slit spectrographs such as \IRIS~\citep{DePontieu2014}, whose \FOV\
    and cadence catch only a few events, while imagers with a wide \FOV\ measure no velocity at all.
\item \textbf{Snapshot spectroscopy.}
    A \CTIS\ records dispersed images of a wide \FOV\ at once~\citep{Okamoto1991,Descour1995}.
    \MOSESCapital~\citep{Kankelborg2001,Fox2010} and \ESIS~\citep{Parker2022} demonstrated the technique
    in the \EUV.
    \ESISI\ flew on 2019 September 30 with four channels in \OV\ \SI{630}{\angstrom}, and
    recovered the Doppler shifts of explosive events, compact sources which act as their own slit.
    Extended structures were harder to validate.
\item \textbf{\ESISII.}
    The same concept, with new optics for \NeVII\ and \SiXII\ and six channels, to observe an \AR.
    \roy{Planned launch date and range.}
\item \textbf{Roadmap.}
    Section~\ref{sec:ScientificMotivation} motivates the passband,
    Section~\ref{sec:TheESISIIInstrument} describes the instrument and what has changed since
    \ESISI, Section~\ref{sec:InversionsofTestData} inverts test data, and
    Section~\ref{sec:Conclusions} concludes.
\end{outline}""")
    return result
