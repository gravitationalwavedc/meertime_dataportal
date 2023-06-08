from decimal import Decimal
import datetime


def mjd_to_datetime(mjd_string):
    mjd = float(mjd_string)
    unix_timestamp = (mjd - 40587) * 86400
    datetime_obj = datetime.datetime.utcfromtimestamp(unix_timestamp)
    datetime_str = datetime_obj.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    return datetime_str


def convert_frequency_to_period(
        freq: str,
        freq_error: str,
    ):
    """
    Calculate the period from the frequency
    """
    f0 = float(freq)
    f0_err = float(freq_error)

    # Calculate period
    p0 = 1 / f0
    # Calculate the period error
    p0_err = p0 * f0_err / f0

    # Set the precision to be the same decimal places as the error
    p0     = round(p0,     abs(Decimal(p0_err).adjusted()))
    p0_err = round(p0_err, abs(Decimal(p0_err).adjusted()))

    return p0, p0_err



def parse_ephemeris_file(ephemeris_loc):
    # Parse the file by converting it into a dict
    ephemeris_dict = {}
    with open(ephemeris_loc, "r") as file:
        for line in file:
            line = line.strip()
            split_line = line.split()
            # Grab the value
            ephemeris_dict[split_line[0]] = split_line[1]
            if len(split_line) == 4:
                # Also grab the error
                ephemeris_dict[f"{split_line[0]}_ERR"] = split_line[3]

    # Calculate the period from the frequency
    p0, p0_err = convert_frequency_to_period(ephemeris_dict["F0"], ephemeris_dict["F0_ERR"])
    ephemeris_dict["P0"] = p0
    ephemeris_dict["P0_ERR"] = p0_err

    # Convert start and finish to datetime
    ephemeris_dict["START"]  = mjd_to_datetime(ephemeris_dict["START"])
    ephemeris_dict["FINISH"] = mjd_to_datetime(ephemeris_dict["FINISH"])

    return ephemeris_dict