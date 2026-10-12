import aastex

__all__ = [
    "authors",
]


def authors() -> list[aastex.Author]:
    """
    A list of the authors of this article and their affiliations.

    The authors are listed in the order of the science team in the ESIS-2
    proposal.
    """

    gsfc = aastex.Affiliation(
        "NASA Goddard Space Flight Center, " "Greenbelt, MD 20771, USA"
    )
    msfc = aastex.Affiliation(
        "NASA Marshall Space Flight Center, " "Huntsville, AL 35812, USA"
    )
    msu = aastex.Affiliation(
        "Montana State University, "
        "Department of Physics, "
        "P.O. Box 173840, "
        "Bozeman, MT 59717, USA"
    )
    american = aastex.Affiliation(
        "American University, Department of Physics, Washington, DC 20016, USA"
    )

    return [
        aastex.Author(
            name="Jacob D. Parker",
            affiliation=gsfc,
            orcid="0000-0001-8732-8284",
        ),
        aastex.Author(
            name="Genevieve D. Vigil",
            affiliation=msfc,
            orcid="0000-0002-7219-1526",
        ),
        aastex.Author(
            name="Charles C. Kankelborg",
            affiliation=msu,
            orcid="0000-0002-1992-7469",
        ),
        aastex.Author(
            name="Amy R. Winebarger",
            affiliation=msfc,
            orcid="0000-0002-5608-531X",
        ),
        aastex.Author(
            name="Will T. Barnes",
            affiliation=[american, gsfc],
            orcid="0000-0001-9642-6089",
        ),
        aastex.Author(
            name="Roy T. Smart",
            affiliation=msu,
            orcid="0000-0002-9997-5515",
        ),
        aastex.Author(
            name="Adrian N. Daw",
            affiliation=gsfc,
            orcid="0000-0002-9288-6210",
        ),
    ]
