from argparse import ArgumentParser
from parse_cfg import parse_cfg
from db_funcs import connect_to_DB, get_utc_id, get_psr_id, get_proposal_id
import queries as q

import os

import log_sentry


def delete_obs(line, cur):
    """
    deletes an observation from the DB. Input format is a path from the top level of input data, i.e.:
    beam/UTC/PSR
    for example:
    1/2019-11-14-01:48:07/J0835-4510_R

    returns the number of affected rows
    """
    inputs = line.strip().split("/")
    if len(inputs) != 3:
        raise ValueError("malformed input, expected beam/UTC/PSR per line of input file")
    else:
        beam = inputs[0]
        utc = inputs[1]
        psr = inputs[2]
        psr_id = get_psr_id(psr, cur)
        utc_id = get_utc_id(utc, cur)
    deleted_count = cur.execute(q.delete_from_obs_q, [beam, utc_id, psr_id,],)
    if deleted_count != 1:
        print(
            "Warning: observation corresponding to ", line, "resulted in", deleted_count, "deletions",
        )
    return deleted_count


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-c", "--config-dir", dest="configDir", nargs="?", help="Path to mysql config file", default="./",
    )
    parser.add_argument("-i", "--input", nargs="+", help="Input kronos file to parse")
    args = parser.parse_args()

    mysql_cfg = parse_cfg(os.path.join(args.configDir, "mysql.cfg"))
    conn = connect_to_DB(mysql_cfg)
    cur = conn.cursor()

    deleted_count = 0

    for input_fn in args.input:
        with open(input_fn) as in_fh:
            for line in in_fh:
                deleted_count += delete_obs(line, cur)
    print("A total of", deleted_count, "observations were deleted")
