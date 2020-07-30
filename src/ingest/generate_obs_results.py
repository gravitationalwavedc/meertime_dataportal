#!/usr/bin/env python

import sys
import os

from parse_cfg import parse_cfg
import psrchive as psr
import log_sentry


def generate_obs_results(beam, utc, source):

    obs_results_dir = "/fred/oz005/kronos/" + beam + "/" + utc + "/" + source
    if not os.path.exists(obs_results_dir):
        return (False, "results directory did not exist: " + obs_results_dir)

    results_file = obs_results_dir + "/obs.results"
    if os.path.exists(results_file):
        return (True, "results file already exists: " + results_file)

    header_file = obs_results_dir + "/obs.header"
    if not os.path.exists(header_file):
        return (True, "header file did not exist: " + header_file)

    header = parse_cfg(header_file)
    value = -1
    if "PERFORM_FOLD" in header.keys():
        value = header["PERFORM_FOLD"]
    if not value == "1":
        return (True, "observation was not fold mode")

    freq_sum_file = obs_results_dir + "/freq.sum"
    if not os.path.exists(freq_sum_file):
        return (False, "freq.sum file did not exist: " + freq_sum_file)

    time_sum_file = obs_results_dir + "/time.sum"
    if not os.path.exists(time_sum_file):
        return (False, "time.sum file did not exist: " + time_sum_file)

    # determine the snr of the observation
    ar = psr.Archive_load(freq_sum_file)
    ar.remove_baseline()
    ar.dedisperse()
    ar = ar.total()

    snr = ar.get_Profile(0, 0, 0).snr()

    # determine the length of the observation
    length = ar.get_first_Integration().get_duration()

    # write these values to the sum file
    fptr = open(results_file, "w")
    fptr.write("snr\t" + str(snr) + "\n")
    fptr.write("length\t" + str(length) + "\n")
    fptr.close()

    return (True, "Generated obs.results for " + beam + "/" + utc + "/" + source)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("ERROR: 1 command line argument expected")
        sys.exit(1)

    beam_utc_source = sys.argv[1]
    (beam, utc, source) = beam_utc_source.split("/")
    (ok, msg) = generate_obs_results(beam, utc, source)
    if not ok:
        print("ERROR: " + msg)
        sys.exit(1)
    else:
        print(msg)
        sys.exit(0)
