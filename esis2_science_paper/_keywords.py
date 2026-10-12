import aastex

__all__ = [
    "keywords",
]


def keywords() -> aastex.Keywords:
    """
    The Unified Astronomy Thesaurus concepts describing this article.
    """
    return aastex.Keywords(
        [
            aastex.UAT("Solar coronal heating", 1989),
            aastex.UAT("Solar magnetic reconnection", 1504),
            aastex.UAT("Solar active regions", 1974),
            aastex.UAT("Solar transition region", 1532),
            aastex.UAT("Solar extreme ultraviolet emission", 1493),
            aastex.UAT("Solar instruments", 1499),
            aastex.UAT("Spectrometers", 1554),
            aastex.UAT("Doppler shift", 401),
        ]
    )
