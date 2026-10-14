import aastex

__all__ = [
    "acronyms",
]


def acronyms() -> list[aastex.Acronym]:
    """
    A list of acronyms that are used in the body of the article.
    """
    return [
        aastex.Acronym("ESIS", "the EUV Snapshot Imaging Spectrograph"),
        aastex.Acronym("MOSES", "the Multi-Order Solar EUV Spectrograph"),
        aastex.Acronym("IRIS", "the Interface Region Imaging Spectrograph"),
        aastex.Acronym("AIA", "the Atmospheric Imaging Assembly"),
        aastex.Acronym("HiC", "the High-resolution Coronal Imager", "Hi-C"),
        aastex.Acronym("SUTRI", "the Solar Upper Transition Region Imager"),
        aastex.Acronym("EUV", "extreme ultraviolet"),
        aastex.Acronym("TR", "transition region"),
        aastex.Acronym("AR", "active region", short=True, plural=True),
        aastex.Acronym("CTIS", "computed tomography imaging spectrograph", plural=True),
        aastex.Acronym("MART", "multiplicative algebraic reconstruction technique"),
        aastex.Acronym("FOV", "field of view"),
        aastex.Acronym("SNR", "signal-to-noise ratio", short=True),
        aastex.Acronym("DEM", "differential emission measure", plural=True),
        aastex.Acronym("VLS", "varied line spacing"),
        aastex.Acronym("CCD", "charge-coupled device", plural=True),
        aastex.Acronym("QE", "quantum efficiency"),
        aastex.Acronym("DACS", "data acquisition and control system"),
        aastex.Acronym("EVTM", "Ethernet via telemetry"),
        aastex.Acronym("LBNL", "Lawrence Berkeley National Laboratory"),
        aastex.Acronym("WSMR", "White Sands Missile Range"),
    ]
