def get_band(frequency):
    """
    Band is the string representation of the frequency used by astronomers.

    There are 2 bands that most frequencies should fit into. 
    UHF: Ultra High Frequency in the range 300 MHZ to 1 GHZ
    L-BAND: Freqencies unfortunately used for GPS in the range 1 to 2 GHZ
    """
    try:
        if abs(frequency - 830) < 200:
            return "UHF"
        elif abs(frequency - 1285) < 200:
            return "L-band"
        return str(frequency)
    except TypeError:
        return None


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
