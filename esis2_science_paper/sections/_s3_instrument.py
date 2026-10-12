import aastex

__all__ = [
    "instrument",
]


def instrument() -> aastex.Section:
    """
    The section describing ESIS-2, mostly in terms of what has changed since
    the first flight.
    """
    result = aastex.Section(aastex.NoEscape(r"The \ESIStwo\ Instrument"))
    result.append(r"""
\begin{outline}
\item A six-channel \CTIS: a parabolic primary mirror images the Sun onto an octagonal field stop,
    which six gratings re-image onto six \CCDs, each channel dispersing in a different direction.
\item Describe only what has changed.
    The heritage design is described in the \ESISone\ instrument paper (Smart et al., in
    preparation). \roy{Cite once it is on arXiv.}
\item The design has changed considerably since the proposal.
    Every number comes from the current \ESIStwo\ model, \texttt{esis.flights.f2}, in the
    \texttt{esis} package.
\end{outline}""")

    subsection_changes = aastex.Subsection("Changes Since the First Flight")
    subsection_changes.append(r"""
\begin{outline}
\item \textbf{New:} the passband; a primary mirror with a longer focal length, which uses the full
    length of the optical table now that \MOSES\ is gone from it; new gratings; Al/Sc multilayer
    coatings; two more channels; filters moved to suit the slower beam; the telemetry interface
    (\EVTM).
\item \textbf{Reused:} the cameras of \ESISone, the \DACS, and the ground support equipment.
    \jake{What else carries over unchanged: the field stop mount, the grating mounts, the camera
    mount?}
\item \textbf{Table:} each subsystem of \ESISone, and whether \ESIStwo\ reuses, modifies, or
    replaces it.
\item \textbf{Figure:} \ESISone\ and \ESIStwo\ on the optical table.
\end{outline}""")
    result.append(subsection_changes)

    subsection_optics = aastex.Subsection("Optical Design")
    subsection_optics.append(r"""
\begin{outline}
\item The primary mirror moves aft and the gratings forward on the optical table, lengthening the
    focal length of the primary for a finer plate scale.
    The field stop moves to the new focus.
\item The radius, tilt, and \VLS\ ruling of the gratings, first estimated from the grating equation
    and \citet{Poletto2004}, then optimized for \NeVII\ and \SiXII.
    The gratings are blazed.
\item \NeVII\ and \SiXII\ fall on opposite sides of the center of each detector without
    overlapping.
\item The six channels take the azimuths of the six-channel layout for which \ESISone\ was built.
\item Plate scale, dispersion, and resolution from the raytrace.
\item \textbf{Table:} the optical prescription.
\item \textbf{Figures:} the layout of the six channels and their dispersion directions; spot
    diagrams across the \FOV\ at both wavelengths.
\end{outline}""")
    result.append(subsection_optics)

    subsection_coatings = aastex.Subsection("Multilayer Coatings and Filters")
    subsection_coatings.append(r"""
\begin{outline}
\item The primary mirror and the gratings both need multilayers which reflect \NeVII\ and \SiXII\
    well and suppress \SIrange{215}{267}{\angstrom}, which would otherwise reach the detector in
    second order.
\item Al/Sc multilayers~\citep{Rebellato2020,Rebellato2021} on both, compared with the Si/Sc
    alternative used for \NeVII\ by \SUTRI~\citep{Bai2023,Wu2022}.
    Designs modeled with IMD~\citep{Windt1998}, and the reflectance of witness samples.
\item Filters: the \ESISone\ design, with the transmission modeled including an oxide layer.
\item \textbf{Figure:} the reflectance of the coatings and the transmission of the filters versus
    wavelength.
\end{outline}""")
    result.append(subsection_coatings)

    subsection_cameras = aastex.Subsection("Cameras and Avionics")
    subsection_cameras.append(r"""
\begin{outline}
\item The cameras of \ESISone\ and the new cameras which make up six.
    The readout sets the cadence, \cadence, with no dead time between exposures.
\item Gain, read noise, and dark current of all six cameras. \roy{Measured with
    \texttt{msfc-ccd}.}
\item The \DACS, with new cables for the new cameras and telemetry through \EVTM.
\end{outline}""")
    result.append(subsection_cameras)

    subsection_mechanical = aastex.Subsection("Mechanical Changes")
    subsection_mechanical.append(r"""
\begin{outline}
\item The new positions of the primary mirror, field stop, gratings, and filters on the optical
    table, and the effect on the sag of the table measured while aligning \ESISone.
\item The \ESISone\ primary mirror shifted by about \ang{;10;} in vibration testing, and how the
    \ESIStwo\ mount prevents that. \jake{Is the stiffer mount from the proposal still the plan?}
\end{outline}""")
    result.append(subsection_mechanical)

    subsection_alignment = aastex.Subsection("Alignment and Focus")
    subsection_alignment.append(r"""
\begin{outline}
\item The \ESISone\ procedure, with a visible-light alignment grating for each channel whose
    ruling is scaled by the ratio of the HeNe wavelength to the center of the passband, so that
    \SI{632.8}{\nano\meter} light follows the path of the \EUV.
\item Establish the optic axis; align the primary mirror; place the field stop at its focus;
    align each grating to its \CCD; focus each \CCD; transfer the alignment from the visible
    gratings to the \EUV\ gratings.
\item \roy{As-measured alignment and focus, once the instrument is aligned.}
\end{outline}""")
    result.append(subsection_alignment)

    subsection_area = aastex.Subsection("Effective Area and Expected Count Rates")
    subsection_area.append(r"""
\begin{outline}
\item Effective area from the geometric area, the reflectance of the two coatings, the groove
    efficiency, the filter transmission, and the \QE\ of the \CCD, compared with the requirement of
    Section~\ref{subsec:Requirements}.
\item Expected count rates from an \AIA\ \DEM~\citep{Cheung2015} of an example \AR, and the \SNR\
    of a single exposure across the \FOV.
\item \textbf{Figures:} the effective area versus wavelength; a simulated image from one channel.
\end{outline}""")
    result.append(subsection_area)

    subsection_operations = aastex.Subsection("Concept of Operations")
    subsection_operations.append(r"""
\begin{outline}
\item Launch from \WSMR, with the target \AR\ chosen the day before.
\item The cameras expose continuously every \cadence; frames taken before the door opens and after
    it closes are darks.
\item Uplink commands can restart the cameras or repoint the payload.
    Only a subset of the frames is telemetered, so the payload must be recovered.
\end{outline}""")
    result.append(subsection_operations)

    return result
