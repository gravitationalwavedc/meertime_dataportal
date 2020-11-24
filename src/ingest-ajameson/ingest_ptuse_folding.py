#!/usr/bin/env python

import glob
import numpy as np
import logging
import time
import os
import json

import database
from util import header, ephemeris

RESULTS_DIR = 'test_data/kronos'
FOLDING_DIR = 'test_data/timing'
LOG_DIRECTORY = "logs"
LOG_FILE = "%s/%s" % (LOG_DIRECTORY, time.strftime("%Y-%m-%d_c2g_receiver.log"))


def main(beam, utc, source, freq):

    obs_type = "fold"
    results_dir = "%s/%s/%s/%s" % (RESULTS_DIR, beam, utc_start, source)

    # results directory
    obs_header = "%s/obs.header" % (results_dir)
    if not os.path.isfile(obs_header):
        error = Exception("%s not found." % obs_header)
        logging.error(str(error))
        raise error

    try:
        hdr = header.PTUSEHeader(obs_header)
    except Exception as error:
        logging.error(str(error))
        raise error
    hdr.set("BEAM", beam)
    hdr.parse()

    try:
        obs_results = header.KeyValueStore("%s/obs.results" % (results_dir))
    except Exception as error:
        logging.error(str(error))
        raise error

    try:
        db = database.PsrDataBase()
    except Exception as error:
        logging.error(str(error))
        raise error

    # add this pulsar to the database if not already existing
    targets = database.Targets(db)
    target_id = targets.get_id(hdr, create=True)
    logging.info("target_id=%d" % (target_id))

    pulsars = database.Pulsars(db)
    pulsar_id = pulsars.get_id(hdr, create=True)
    logging.info("pulsar_id=%d" % (pulsar_id))

    pulsartargets = database.PulsarTargets(db)
    pulsartargets.get_pulsar_target(pulsar_id, target_id, create=True)

    telescopes = database.Telescopes(db)
    telescope_id = telescopes.get_id(hdr, create=True)
    logging.info("telescope_id=%d" % (telescope_id))

    instrument_configs = database.InstrumentConfigs(db)
    instrument_config_id = instrument_configs.get_id(hdr, create=True)
    logging.info("instrument_config_id=%d" % (instrument_config_id))

    # estimate the duration of the observation
    duration = float(obs_results.get("length"))
    observations = database.Observations(db)
    observation_id = observations.get_id(
        target_id, utc_start, duration, obs_type, telescope_id, instrument_config_id, create=True
    )
    logging.info("observation_id=%d" % (observation_id))

    ptuse_calibrations = database.PTUSECalibrations(db)
    ptuse_calibration_id = ptuse_calibrations.get_id(utc_start, create=True)
    logging.info("ptuse_calibration_id=%d" % (ptuse_calibration_id))

    ptuse_configs = database.PTUSEConfigs(db)
    ptuse_config_id = ptuse_configs.get_id(observation_id, ptuse_calibration_id, hdr, create=True)

    eph = ephemeris.Ephemeris()
    eph_fname = "%s/%s/%s/%s/pulsar.eph" % (RESULTS_DIR, beam, utc_start, source)
    eph.load_from_file(eph_fname)

    ephemerides = database.Ephemerides(db)
    ephemeris_id = ephemerides.get_id(pulsar_id, eph, create=True)
    logging.info("ephemeris_id=%d" % (ephemeris_id))

    pipelines = database.Pipelines(db)

    parent_pipeline_id = pipelines.get_id("Orphan Master", "None", "{}", create=True)
    logging.info("parent_pipeline=%d" % (parent_pipeline_id))

    pipeline_id = pipelines.get_id(hdr.machine, hdr.machine_version, hdr.machine_config, create=True)
    logging.info("pipeline=%d" % (pipeline_id))

    location = "%s/%s/%s/%s/%s/" % (FOLDING_DIR, beam, source, utc_start, freq)
    results = {"snr": float(obs_results.get("snr"))}
    processings = database.Processings(db)
    processing_id = processings.get_id(
        observation_id, pipeline_id, parent_pipeline_id, location, json.dumps(results), create=True
    )
    logging.info("processing_id=%d" % (processing_id))

    foldings = database.Foldings(db)
    folding_id = foldings.get_id(processing_id, ephemeris_id, hdr, create=True)
    logging.info("folding_id=%d" % (folding_id))

    # process image results for this observations
    pipelineimages = database.PipelineImages(db)
    rank = 0
    image_class = "blah"
    for png in glob.glob("%s/*.hi.png" % (results_dir)):
        pipeline_image_id = pipelineimages.get_id(processing_id, rank, image_class, png, create=True)
        rank += 1
        logging.info("pipeline_image_id=%d" % (pipeline_image_id))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Ingest PTUSE fold mode observation')
    parser.add_argument('beam', type=str, help='beam number')
    parser.add_argument('utc_start', type=str, help='utc_start of the obs')
    parser.add_argument('source', type=str, help='source of the obs')
    parser.add_argument('freq', type=str, help='coarse centre frequency of the obs in MHz')
    args = parser.parse_args()

    beam = args.beam
    utc_start = args.utc_start
    source = args.source
    freq = args.freq

    format = "%(asctime)s : %(levelname)s : " + "%s/%s/%s/%s" % (beam, utc_start, source, freq) + " : %(msg)s"
    # logging.basicConfig(format=format,filename=LOG_FILE,level=logging.INFO)
    logging.basicConfig(format=format, level=logging.DEBUG)

    main(beam, utc_start, source, freq)
