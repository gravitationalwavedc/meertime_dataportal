#!/usr/bin/env python

from argparse import ArgumentParser
from parse_cfg import parse_cfg
from db_funcs import connect_to_DB, get_utc_id, get_psr_id, get_proposal_id
import queries as q
import proposals

import os

import log_sentry


def parse_kronos_line(line, cur):
    inputs = line.split()
    if len(inputs) == 14 and inputs[13] == "0":
        utc = inputs[0]
        psr = inputs[1]
        beam = inputs[2]
        DM = inputs[3]
        snr = inputs[4]
        length = inputs[5]
        nchan = inputs[6]
        nbin = inputs[7]
        nant = inputs[8]
        nant_eff = inputs[9]
        proposal = inputs[10]
        bw = inputs[11]
        freq = inputs[12]
        proposal = proposals.fix_proposal(proposal)

        psr_id = get_psr_id(psr, cur)
        utc_id = get_utc_id(utc, cur)
        proposal_id = get_proposal_id(proposal, cur)

        cur.execute(
            q.insert_update_kronos_fold_obs_q,
            [
                psr_id,
                utc_id,
                proposal_id,
                nchan,
                nbin,
                nant,
                nant_eff,
                beam,
                DM,
                length,
                snr,
                bw,
                freq,
                beam,
                DM,
                snr,
                proposal_id,
                nant_eff,
                length,
                bw,
                freq,
            ],
        )

    elif len(inputs) == 11 and inputs[10] == "0":
        psr = inputs[1]
        if psr[-1] in ["O", "N", "S"]:
            utc = inputs[0]
            beam = inputs[2]
            snr = inputs[3]
            length = inputs[4]
            nchan = inputs[5]
            nbin = inputs[6]
            nant = inputs[7]
            nant_eff = inputs[8]
            proposal = inputs[9]

            psr_id = get_psr_id(psr, cur)
            utc_id = get_utc_id(utc, cur)
            proposal_id = get_proposal_id(proposal, cur)

            cur.execute(
                q.insert_update_kronos_fluxcal_q,
                [
                    psr_id,
                    utc_id,
                    proposal_id,
                    nchan,
                    nbin,
                    nant,
                    nant_eff,
                    beam,
                    length,
                    snr,
                    beam,
                    snr,
                    proposal_id,
                    nant_eff,
                ],
            )
        else:
            print("fluxcal-like observation but unexpected souce name ", psr)
            return -1

    elif len(inputs) == 17 and inputs[16] == "1":
        utc = inputs[0]
        psr = inputs[1]
        beam = inputs[2]
        ra = inputs[3]
        dec = inputs[4]
        DM = inputs[5]
        nbit = inputs[6]
        nchan = inputs[7]
        npol = inputs[8]
        tsamp = inputs[9]
        nant = inputs[10]
        nant_eff = inputs[11]
        proposal = inputs[12]
        proposal = proposals.fix_proposal(proposal)
        length = inputs[13]
        bw = inputs[14]
        freq = inputs[15]
        try:
            float(length)
        except ValueError:
            length = "-1"

        psr_id = get_psr_id(psr, cur)
        utc_id = get_utc_id(utc, cur)
        proposal_id = get_proposal_id(proposal, cur)

        cur.execute(
            q.insert_update_kronos_search_obs_q,
            [
                psr_id,
                utc_id,
                proposal_id,
                nchan,
                nbit,
                npol,
                nant,
                nant_eff,
                beam,
                DM,
                bw,
                freq,
                length,
                tsamp,
                ra,
                dec,
                length,
                nant_eff,
            ],
        )

    else:
        # needs handling
        print("Unknown observation type", len(inputs))
        print(inputs)
        return -1

    return 0


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c",
        "--config-dir",
        dest="configDir",
        nargs="?",
        help="Path to mysql config file",
        default="./",
    )
    parser.add_argument("-i", "--input", nargs="+", help="Input kronos file to parse")
    args = parser.parse_args()

    mysql_cfg = parse_cfg(os.path.join(args.configDir, "mysql.cfg"))
    conn = connect_to_DB(mysql_cfg)
    cur = conn.cursor()

    for input_fn in args.input:
        with open(input_fn) as in_fh:
            for line in in_fh:
                parse_kronos_line(line, cur)
