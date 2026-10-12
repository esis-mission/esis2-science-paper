import aastex

__all__ = [
    "abstract",
]


def abstract() -> aastex.Abstract:
    result = aastex.Abstract()
    result.append(r"""
Nanoflare models of active region heating predict that coronal magnetic reconnection accelerates
beams of nonthermal electrons, which deposit their energy in the transition region at the
footpoints of hot loops, the moss.
Beam heating brightens the moss for tens of seconds and blue-shifts its transition region lines,
which heating by thermal conduction does not.
Slit spectrographs have observed these signatures only when their slit happened to cross an event,
since they cannot measure velocity across a wide field of view at a rapid cadence.
A computed tomography imaging spectrograph (CTIS) can: it records several dispersed images of the
same field at once, from which the intensity, Doppler shift, and width of an emission line can be
recovered everywhere in a single exposure.
We describe the second flight of the EUV Snapshot Imaging Spectrograph (\ESIStwo), a sounding rocket
CTIS which will observe an active region in \NeVII\ \SI{465}{\angstrom} and \SiXII\ \SI{499}{\angstrom},
formed near \temperatureNeVII\ and \temperatureSiXII\ respectively, across a \fieldOfView\ field of
view every \cadence.
Hydrodynamic simulations show that \NeVII\ discriminates between beam and conductive heating, while
\SiXII\ images extended coronal loops, the structures that are hardest for a CTIS to invert.
\ESIStwo\ reuses the cameras and avionics of the first flight, with new optics for the new
passband: a primary mirror with a longer focal length, new gratings, and Al/Sc multilayer coatings,
and two more channels for a total of six.
We invert simulated \ESIStwo\ observations with the multiplicative algebraic reconstruction
technique and with a convolutional neural network using subsets of the six channels, and find that
\numChannelsRequired\ channels recover the Doppler shifts of extended structures to within
\velocityError.
\roy{One sentence on what this means for the flight and for a future orbital CTIS.}
\acresetall""")
    return result
