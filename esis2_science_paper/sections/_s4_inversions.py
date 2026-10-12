import aastex

__all__ = [
    "inversions",
]


def inversions() -> aastex.Section:
    """
    The section inverting test data to validate the inversion of extended
    structures, the technology objective of ESIS-II.
    """
    result = aastex.Section("Inversions of Test Data")
    result.append(r"""
\begin{outline}
\item The test data are simulated \ESISII\ observations of scenes whose line profiles are known,
    so the inversions can be compared with the truth.
\end{outline}""")

    subsection_data = aastex.Subsection("Test Data")
    subsection_data.append(r"""
\begin{outline}
\item Scenes with known line profiles: \IRIS\ \SiIV\ rasters of \ARs\ rescaled to
    \NeVII~\citep{DePontieu2014}; \AIA\ images given the radiance and width of
    \SiXII; and beam heating events from the HYDRAD simulations inserted into the moss.
    The first two are \texttt{esis.data.synth.scene\_iris} and \texttt{scene\_aia}.
\item Forward modeled through \texttt{esis.flights.f2}, with photon and read noise for a single
    exposure.
\item \textbf{Figure:} a simulated image from every channel.
\end{outline}""")
    result.append(subsection_data)

    subsection_methods = aastex.Subsection("Inversion Methods")
    subsection_methods.append(r"""
\begin{outline}
\item \MARTCapital~\citep{Gordon1970}, as applied to \ESISI~\citep[][Appendix~B]{Parker2022}:
    multiplicative updates keep the solution positive and assume no line shape, and regularization
    suppresses the ``plaid'' artifacts along the projection directions.
\item A \CNN\ trained on \IRIS\ rasters, after Smart et al.\ (2022) \roy{bib entry for the TESS
    abstract}, retrained on the \ESISII\ forward model.
\item Both are implemented in \texttt{ctis}.
\end{outline}""")
    result.append(subsection_methods)

    subsection_experiments = aastex.Subsection("Validation Experiments")
    subsection_experiments.append(r"""
\begin{outline}
\item Invert using every subset of three or more channels, and compare the recovered moments with
    each other and with the truth.
\item Invert using a subset, forward model the withheld channels, and compare them with the
    simulated observations.
    Only this experiment can be repeated with the flight data, so the test data calibrate how well
    the withheld-channel residual predicts the true error.
\item Error in intensity, Doppler shift, and width versus the number of channels, separately for
    compact brightenings in \NeVII\ and extended loops in \SiXII.
\end{outline}""")
    result.append(subsection_experiments)

    subsection_results = aastex.Subsection("Results")
    subsection_results.append(r"""
\begin{outline}
\item Compact \NeVII\ brightenings: whether the blue shifts of beam heating events are recovered
    with few channels, as for the explosive events of \ESISI~\citep{Parker2022}.
\item Extended \SiXII\ structures: \numChannelsRequired\ channels recover the Doppler shift to
    within \velocityError.
\item \textbf{Figures:} recovered versus true moments; error versus the number of channels.
\end{outline}""")
    result.append(subsection_results)

    return result
