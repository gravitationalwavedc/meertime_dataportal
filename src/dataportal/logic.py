bands = {
    "UHF": {"centre_frequency": 830.0, "allowed_deviation": 200.0,},
    "L-band": {"centre_frequency": 1285.0, "allowed_deviation": 200.0,},
    "S-band": {"centre_frequency": 2625.0, "allowed_deviation": 200.0,},
}


def get_band(frequency):
    """
    Band is the string representation of the frequency used by astronomers.

    There are 3 bands that most frequencies should fit into.
    UHF: Ultra High Frequency / 50-cm band, in the range 300 MHZ to 1 GHZ
    L-band: 20-cm band, around Hydrogen transition line ~1.42 GHz
    S-band: 10-cm band, around 2.6 GHz
    """
    try:
        for band in bands.keys():
            if abs(frequency - bands[band]["centre_frequency"]) < bands[band]["allowed_deviation"]:
                return band
        return str(round(frequency, 1))
    except TypeError:
        return None


def get_band_filters(band=None, prefix=""):
    band_filter = {}
    if band:
        if band not in bands.keys():
            return band_filter
        if prefix:
            prefix = prefix + "__"
        band_filter = {
            f"{prefix}frequency__gte": bands[band]["centre_frequency"] - bands[band]["allowed_deviation"],
            f"{prefix}frequency__lte": bands[band]["centre_frequency"] + bands[band]["allowed_deviation"],
        }
    return band_filter


def get_meertime_filters(prefix=""):
    """
    Creates a filter dictionary which can be passed on to django ORM filter method.
    prefix: (optional) if the proposal model is not directly accessible, provide the model via which it can be accessed
    """
    if prefix:
        prefix = prefix + "__"
    proposal_filter = {
        f"{prefix}proposal__proposal__startswith": "SCI",
        f"{prefix}proposal__proposal__contains": "MB",
    }
    return proposal_filter
