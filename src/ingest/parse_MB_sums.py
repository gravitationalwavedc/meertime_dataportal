#!/usr/bin/env python

# WARNING: this implementation does NOT use prepared statements

from argparse import ArgumentParser
from parse_cfg import parse_cfg
from db_funcs import connect_to_DB, get_utc_id, get_psr_id
import queries as q

import os

import log_sentry


def parse_line(line, cur):
    inputs = line.split()
    if len(inputs) < 19:
        # raise an error
        return -1
    dir = inputs[0]
    utc = inputs[1]
    tint = inputs[3]
    bw = inputs[4]
    freq = inputs[5]
    RM = inputs[6]
    DM = inputs[7]
    psr = inputs[8]
    nchan = inputs[9]
    nbin = inputs[10]  # ignored currently
    MJD = inputs[11]
    MJD_int = inputs[12]
    MJD_frac = inputs[13]
    PA = inputs[14]
    RA = inputs[15]
    DEC = inputs[16]
    index = 17
    if len(inputs) == 20:
        observer = inputs[index]
        index += 1
    else:
        observer = "unknown"
    snr = inputs[index]
    index += 1
    nant = inputs[index]  # ignored currently

    psr_id = get_psr_id(psr, cur)
    utc_id = get_utc_id(utc, cur)

    cur.execute(
        q.insert_update_processed_obs_q,
        [
            psr_id,
            utc_id,
            tint,
            bw,
            freq,
            RM,
            DM,
            nchan,
            nbin,
            nant,
            MJD,
            MJD_int,
            MJD_frac,
            PA,
            RA,
            DEC,
            observer,
            snr,
            tint,
            bw,
            freq,
            RM,
            DM,
            nchan,
            nbin,
            nant,
            MJD,
            MJD_int,
            MJD_frac,
            PA,
            RA,
            DEC,
            observer,
            snr,
        ],
    )
    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config-dir", dest="configDir", nargs="?", help="Path to mysql config file", default="./",
    )
    parser.add_argument("-i", "--input", nargs="+", help="Input file to parse")
    args = parser.parse_args()

    mysql_cfg = parse_cfg(os.path.join(args.configDir, "mysql.cfg"))
    conn = connect_to_DB(mysql_cfg)
    cur = conn.cursor()

    for input_fn in args.input:
        with open(input_fn) as in_fh:
            for line in in_fh:
                parse_line(line, cur)

    conn.commit()
