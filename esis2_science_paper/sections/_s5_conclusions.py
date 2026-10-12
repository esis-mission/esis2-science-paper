import aastex

__all__ = [
    "conclusions",
]


def conclusions() -> aastex.Section:
    result = aastex.Section("Conclusions")
    result.append(r"""
\begin{outline}
\item How the \NeVII\ and \SiXII\ passband serves the two science objectives and the technology
    objective.
\item What changed since \ESISI, and the readiness of the instrument for flight.
\item The minimum number of channels found by the inversions, and what it implies for a future
    orbital \CTIS.
\item The data products, Levels 0 through 3, and the software which makes them, released through
    the \texttt{esis} package and the Solar Data Analysis Center.
\end{outline}""")
    return result
