bands = {
    "UHF": {
        "centre_frequency": 830.0,
        "allowed_deviation": 200.0,
    },
    "L-band": {
        "centre_frequency": 1285.0,
        "allowed_deviation": 200.0,
    },
    "S-band": {
        "centre_frequency": 2625.0,
        "allowed_deviation": 200.0,
    },
}


def get_band(frequency):
    """
    Band is the string representation of the frequency used by astronomers.

    There are 3 bands that most frequencies should fit into.
    UHF: Ultra High Frequency / 50-cm band, in the range 300 MHZ to 1 GHZ
    L-band: 20-cm band, around Hydrogen transition line ~1.42 GHz
    S-band: 10-cm band, around 2.6 GHz
    """
    # For band check to work the frequency must be either an int or a float.
    if type(frequency) not in [float, int]:
        return None

    for band in bands.keys():
        if abs(frequency - bands[band]["centre_frequency"]) < bands[band]["allowed_deviation"]:
            return band

    return str(round(frequency, 1))


def get_band_filters(band=None, prefix=None):
    """
    Creates dictionary of filters that can be passed to a django query filter method.
    band: (optional) A string representation of a band.
    prefix: (optional) if the proposal model is not directly accessible, provide the model via which it can be accessed.
    """
    if band not in bands.keys():
        return {}

    prefix = f"{prefix}__" if prefix else ""

    return {
        f"{prefix}frequency__gte": bands[band]["centre_frequency"] - bands[band]["allowed_deviation"],
        f"{prefix}frequency__lte": bands[band]["centre_frequency"] + bands[band]["allowed_deviation"],
    }


def get_meertime_filters(prefix=None):
    """
    Creates a filter dictionary which can be passed on to django ORM filter method.
    For a proposal to be included in the meertime observation list it must start with SCI and include MB.

    prefix: (optional) if the proposal model is not directly accessible, provide the model via which it can be accessed.
    """
    prefix = f"{prefix}__" if prefix else ""

    return {
        f"{prefix}project__code__startswith": "SCI",
        f"{prefix}project__code__contains": "MB",
    }


def get_trapum_filters(prefix=None):
    """
    Creates a filter dictionary which can be passed on to django ORM filter method.
    For a proposal to be included in the trapum observation list it must start with SCI and include MK.

    prefix: (optional) if the proposal model is not directly accessible, provide the model via which it can be accessed.
    """
    prefix = f"{prefix}__" if prefix else ""

    return {
        f"{prefix}project__code__startswith": "SCI",
        f"{prefix}project__code__contains": "MK",
    }
