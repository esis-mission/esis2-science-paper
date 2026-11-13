# first line: 75
@_memory.cache
def _muram(
    fraction_min: float,
    velocity: u.Quantity,
    num_chunk: int,
    wavelength: u.Quantity,
    versions: dict[str, str],
) -> tuple[na.FunctionArray, na.FunctionArray, na.FunctionArray, na.AbstractScalar]:
    """
    Compute and remember the simulated exposure of the scene, the radiance
    and the Doppler centroid of the lines nearest `wavelength`, and the rest
    wavelength of every line of the scene.

    It takes tens of minutes, mostly imaging each line in each group of bins
    of velocity.

    The results are single precision, which halves what is committed and is
    far finer than the figure can show.

    ``versions`` is not read here, but is part of the key the cache is looked
    up by: it holds the versions of the packages and of the CHIANTI database
    the image is computed with.
    """
    velocity = na.ScalarArray(velocity, axes="velocity")
    wavelength = na.ScalarArray(wavelength, axes=_axis_target)

    instrument = esis.flights.f2.optics.design_single(num_distribution=0)

    # One linear approximation of the instrument across the whole passband,
    # as for the image of the scene from AIA.
    linear = instrument.system.linearize(
        wavelength=na.linspace(
            start=instrument.wavelength_min,
            stop=instrument.wavelength_max,
            axis="_wavelength",
            num=105,
        ),
        degree=2,
        degree_distortion=3,
    )

    # The scene is computed for a group of bins of velocity at a time, and
    # each of its lines imaged one at a time, as for the image of the scene
    # from AIA. Each is exposed with its own shot noise but not integrated
    # over wavelength, so that the read noise is added once, for the single
    # readout of the sensor.
    axis_field = (_axis_x, _axis_y)
    num_bin = velocity.shape["velocity"] - 1
    electrons = 0
    radiance = 0
    moment = 0
    for k in range(0, num_bin, num_chunk):
        v = velocity[{"velocity": slice(k, k + num_chunk + 1)}]
        scene = esis.flights.f2.data.synth.scene_muram(
            velocity=v,
            fraction_min=fraction_min,
            axis_x=_axis_x,
            axis_y=_axis_y,
        )

        # the radiance of the lines nearest `wavelength`, and its first
        # moment in velocity
        rest = scene.inputs.wavelength_rest
        index = np.argmin(np.abs(rest - wavelength), axis="line")
        width = scene.inputs.wavelength.volume_cell("velocity")[index]
        spectrum = scene.outputs[index]
        center = v.cell_centers("velocity")
        radiance = radiance + na.vecdot(spectrum, width, axis="velocity")
        moment = moment + na.vecdot(spectrum, width * center, axis="velocity")

        for i in range(rest.shape["line"]):
            line = scene[{"line": i}].explicit
            weights = linear.weights(
                coordinates=line.inputs,
                axis_wavelength="velocity",
                axis_field=axis_field,
            )
            image = linear.image_from_weights(
                weights,
                line,
                axis_wavelength="velocity",
                axis_field=axis_field,
                integrate=False,
            )
            electrons = electrons + image.outputs.sum("velocity")

    # the single readout of the sensor
    electrons = na.random.normal(loc=electrons, scale=linear.sensor.read_noise)

    position = scene.inputs.position
    image = na.FunctionArray(
        inputs=image.inputs.position,
        outputs=electrons.to(u.electron).astype(np.float32),
    )
    centroid = na.FunctionArray(
        inputs=position,
        outputs=(moment / radiance).to(u.km / u.s).astype(np.float32),
    )
    radiance = na.FunctionArray(
        inputs=position,
        outputs=radiance.to(u.erg / u.cm**2 / u.s / u.sr).astype(np.float32),
    )

    return image, radiance, centroid, rest
