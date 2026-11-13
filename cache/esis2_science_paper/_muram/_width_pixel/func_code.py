# first line: 238
@_memory.cache
def _width_pixel(version: str) -> u.Quantity:
    """
    Read and remember the width of a pixel of the simulation.

    Remembered beside the image, so that only the computer which computes
    the image downloads the simulation.

    ``version`` is not read here, but is part of the key the cache is looked
    up by: it is the version of ``esis``, which names the simulation.
    """
    store = zarr.open_group(esis.flights.f2.data.synth.path_muram(), mode="r")
    x = store["x"][:] * u.cm
    return x[1] - x[0]
