import aastex

__all__ = [
    "motivation",
]


def motivation() -> aastex.Section:
    """
    The section motivating the passband of ESIS-2 from its science objectives.
    """
    result = aastex.Section("Scientific Motivation")

    subsection_moss = aastex.Subsection("Electron Beam Heating in Active Region Moss")
    subsection_moss.append(r"""
\begin{outline}
\item Moss is the reticulated \TR\ emission at the footpoints of the hot loops in \AR\
    cores~\citep{Berger1999}.
    Its intensity is proportional to the pressure of the loop, so it is a sensitive gauge of
    coronal heating~\citep{Martens2000}.
\item Moss was long found to be steady~\citep{Antiochos2003,Brooks2009}: either the heating is
    quasi-steady, or the events were smaller or shorter than earlier instruments could resolve.
\item \HiCCapital~\citep{Kobayashi2014} found moss brightening on timescales of about
    \SI{15}{\second}, at the footpoints of loops which appeared shortly afterward in the hotter
    \AIA~\citep{Lemen2012} channels~\citep{Testa2013}.
\item \citet{Testa2014} combined \IRIS, \AIA, and models: \TR\ brightenings lasted
    \SIrange{20}{60}{\second}, brightened by up to two orders of magnitude, and showed \SiIV\ blue
    shifts on the few occasions the slit crossed an event.
    Beams deposit their energy below the height at which \SiIV\ forms and blue-shift it, while
    conduction red-shifts it.
\item The response depends on the beam parameters and on the initial state of the loop, and beams
    do not always blue-shift the line, but a blue shift is a clear sign of a beam~\citep{Polito2018}.
    \citet{Testa2023} constrained the beam parameters by comparing observations with models.
\item The best discriminator, \TR\ velocity, is limited by the \FOV\ and cadence of slit
    spectrographs.
\item \textbf{Figure:} an \AR\ in \AIA, showing the moss and the hot core.
\end{outline}""")
    result.append(subsection_moss)

    subsection_objectives = aastex.Subsection("Science and Technology Objectives")
    subsection_objectives.append(r"""
\begin{outline}
\item \textbf{Science goal:} determine the role of magnetic reconnection in heating the corona.
\item \textbf{Science Objective 1:} determine the frequency and spatial location of heating by
    electron beams, from intensity and velocity measured simultaneously over a wide \FOV.
\item \textbf{Science Objective 2:} determine the heating parameters (timescale, total energy, and
    low-energy cutoff of the beam) of every beam heating event, by comparison with hydrodynamic
    models~\citep{Testa2023}.
\item \textbf{Technology objective:} validate the inversion of two-dimensional extended structures
    observed with a \CTIS.
    Compact events can be interpreted with as few as two channels~\citep{Fox2011,Parker2022}, but
    the inversion of extended structures has had no independent check.
    Recovering three moments of the line takes at least three channels, and each additional channel
    is a check on the inversion.
\end{outline}""")
    result.append(subsection_objectives)

    subsection_ctis = aastex.Subsection("Velocity over a Wide Field of View")
    subsection_ctis.append(r"""
\begin{outline}
\item A slitless spectrograph elongates a Doppler-shifted source along its dispersion direction,
    which in a single channel cannot be told apart from a spatial structure lying along that
    direction.
\item The elongation due to velocity rotates with the dispersion direction while spatial structure
    does not, so two channels dispersing in different directions separate them, and their
    difference shows Doppler shifts directly~\citep[][Figures 9--11]{Parker2022}.
\item Compact brightenings act as their own slit, so Science Objectives 1 and 2 can be closed
    without an inversion.
    Extended structures overlap in the dispersed images and must be inverted, which is what the
    technology objective tests.
\item \textbf{Figure:} a cartoon of a compact, Doppler-shifted source and of an extended, stationary
    source, as seen by two channels, and their differences.
\end{outline}""")
    result.append(subsection_ctis)

    subsection_passband = aastex.Subsection("Choice of Passband")
    subsection_passband.append(r"""
\begin{outline}
\item \NeVII\ \SI{465.2}{\angstrom} and \SiXII\ \SI{499.4}{\angstrom} are an order of magnitude
    brighter than any other line between \SIrange{440}{520}{\angstrom}, so their images do not overlap
    and suffer little contamination.
    Spectrum computed from CHIANTI~\citep{Dere1997,DelZanna2021} and an \AR\ \DEM.
\item \NeVII\ forms in the upper \TR, near \temperatureNeVII, hotter than \SiIV.
    \SiXII\ forms in the corona, near \temperatureSiXII, and images the extended loops needed for
    the technology objective.
\item Does \NeVII\ respond to beams as \SiIV\ does?
    HYDRAD~\citep{Bradshaw2013,Reep2013} simulations of a nanoflare whose energy is carried down by
    an electron beam, and of one whose energy is carried down by thermal conduction:
    \NeVII\ is blue-shifted early in the beam case and red-shifted in the conduction case, and its
    intensity decays more slowly in the beam case.
\item Lines between \SIrange{215}{267}{\angstrom} would fall on the passband in second order, so
    the coatings must suppress them (Section~\ref{subsec:MultilayerCoatingsandFilters}).
\item \textbf{Figures:} the \AR\ spectrum across the passband and the contribution functions of
    the two lines; the \NeVII\ intensity and line profile versus time for the beam and conduction
    simulations.
\end{outline}""")
    result.append(subsection_passband)

    subsection_requirements = aastex.Subsection("Requirements")
    subsection_requirements.append(r"""
\begin{outline}
\item \textbf{Table:} the science traceability matrix, from the objectives to the measurement and
    instrument requirements, and the performance expected from the \ESIStwo\ model.
\item \textbf{\FOV\ and cadence:} at least the \FOV\ of \HiC~\citep{Kobayashi2014}, which
    captured beam heating events, and a cadence at least as fast as its \SI{2}{\second}, since \TR\
    velocities can evolve faster than the \SI{4}{\second} \SiIV\ cadence of \citet{Testa2014}.
\item \textbf{Spatial resolution:} a modest resolution suffices, since the brightenings grow by
    two orders of magnitude and the longer ones are visible at the resolution of
    \AIA~\citep{Testa2014}.
    Cadence and \FOV, not resolution, have limited previous observations.
\item \textbf{Dispersion:} enough to separate the \FOV\ of \NeVII\ from that of \SiXII\ on the
    detector.
\item \textbf{\SNRCapital:} 100 photons to measure a velocity, spread over at least three channels, is 36
    photons per channel per resolution element per exposure (an \SNR\ of 6).
    With the radiances of \citet{Vernazza1978}, this sets the required effective area.
\item \textbf{Number of channels:} at least four, three for the moments and one to validate.
\item \textbf{Mission:} an \AR\ on the disk, at least \SI{300}{\second} of observing above
    \SI{150}{\kilo\meter}, stable pointing, and recovery of the payload.
\end{outline}""")
    result.append(subsection_requirements)

    return result
