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
