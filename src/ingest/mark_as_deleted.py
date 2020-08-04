#!/usr/bin/env python

import os
from argparse import ArgumentParser
from parse_cfg import parse_cfg
from db_funcs import connect_to_DB, get_utc_id, get_psr_id, get_proposal_id
import queries as q


def parse_delete_line(line, cur):
    inputs = line.split()
    if len(inputs) == 3:
        utc = inputs[0]
        psr = inputs[1]
        beam = inputs[2]
        psr_id = get_psr_id(psr, cur)
        utc_id = get_utc_id(utc, cur)

        proposal = "DELETED"
        proposal_id = get_proposal_id(proposal, cur)

        result = cur.execute(q.update_proposal, [proposal_id, psr_id, utc_id, beam,])
        if cur.rowcount == 0:
            print("Line:", line.rstrip(), "had no counterpart in Observations table")
            result = cur.execute(q.update_proposal, [proposal_id, psr_id, utc_id, beam,])
            if cur.rowcount == 0:
                print("Line:", line.rstrip(), "had no counterpart in Searchmode table")
            else:
                print("Adjust searchmode obs for", line.rstrip())
        else:
            print("Adjust obs for", line.rstrip())


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config-dir", dest="configDir", nargs="?", help="Path to mysql config file", default="./",
    )
    parser.add_argument("-i", "--input", nargs="+", help="Input kronos file to parse")
    args = parser.parse_args()

    MYSQL_CFG = parse_cfg(os.path.join(args.configDir, "mysql.cfg"))
    conn = connect_to_DB(MYSQL_CFG)
    cur = conn.cursor()

    for input_fn in args.input:
        with open(input_fn) as in_fh:
            for line in in_fh:
                parse_delete_line(line, cur)
