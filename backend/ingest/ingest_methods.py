from datetime import datetime
from base64 import b64decode, b64encode
import sys
import os
import logging
import json

from django.core.files.base import ContentFile
from django.urls import reverse

from .parse_cfg import parse_cfg

from .slack import post_to_slack, post_to_slack_if_meertime


def __setup_django(root_path, settings):
    import django

    os.chdir(root_path)

    # Django settings
    sys.path.append(root_path)
    os.environ["DJANGO_SETTINGS_MODULE"] = settings

    django.setup()


__setup_django(os.environ.get("PWD", "."), "meertime.settings")

from dataportal.models import (
    Observations,
    Searchmode,
    Fluxcal,
    Utcs,
    Pulsars,
    Proposals,
    Ephemerides,
    Schedule,
    PhaseUp,
)


def handle_image_parsing(img_fn):
    """
    This method will read an image file, if a non-empty name was provided.
    It will then encode the contents in base64 and return them.

    If empty file name is provided, return empty string

    Note that '""' is considered an empty string.
    This is to cope with having input data with spaces as separators but
    allow input data with empty parameters
    """
    img_bytes = ""
    if img_fn and img_fn != '""':
        with open(img_fn, "rb") as fh:
            img_bytes = fh.read()
    # provided file name could point to an empty file
    if img_bytes:
        img_bytes = b64encode(img_bytes)

    return img_bytes


def create_ephemeris(psr, updated_at, ephemeris, comment):
    psr, created = Pulsars.objects.get_or_create(jname=psr)
    dt = datetime.strptime(f"{updated_at} +0000", "%Y-%m-%d-%H:%M:%S %z")
    params = {"comment": comment, "updated_at": dt, "ephemeris": ephemeris}

    eph, created = Ephemerides.objects.update_or_create(pulsar=psr, defaults=params)

    msg = f"Ephemeris for {psr} was just updated"
    # this does not need to be checked against proposal code
    post_to_slack(msg)

    return eph


def get_utc_psr_proposal_schedule_phaseup(utc, psr, proposal, schedule, phaseup):
    """
    This method returns foreign keys to UTC, psr, proposal, schedule, and phase up models.
    """
    utc_dt = datetime.strptime(f"{utc} +0000", "%Y-%m-%d-%H:%M:%S %z")
    utc, created = Utcs.objects.get_or_create(utc_ts=utc_dt)
    psr, created = Pulsars.objects.get_or_create(jname=psr)
    proposal, created = Proposals.objects.get_or_create(proposal=proposal)
    if schedule:
        schedule, created = Schedule.objects.get_or_create(schedule=schedule)
    if phaseup:
        phaseup, created = PhaseUp.objects.get_or_create(phaseup=phaseup)
    return utc, psr, proposal, schedule, phaseup


def create_fold_mode(
    utc,
    psr,
    beam,
    RA,
    DEC,
    DM,
    snr,
    length,
    nchan,
    nbin,
    nsubint,
    nant,
    nant_eff,
    proposal,
    bw,
    freq,
    profile,
    phase_vs_time,
    phase_vs_frequency,
    bandpass,
    snr_vs_time,
    schedule=None,
    phaseup=None,
    update=False,
):
    """
    Create or update a fold mode observation.

    If update=False, only new observations will be created.
    Observations have uniqe combination of utc, pulsar, and beam.
    profile, phase_vs_time, phase_vs_frequency, bandpass, and snr_vs time are images
    which are expected to be provided as base64-encoded contents of the images.

    Return a new instance of Observation or None if none was create nor updated.

    update is a boolean but accepts strings "false" and "False" as well
    """
    if update == "false" or update == "False":
        update = False

    # get the foreign keys:
    utc, psr, proposal_obj, schedule, phaseup = get_utc_psr_proposal_schedule_phaseup(
        utc, psr, proposal, schedule, phaseup
    )

    obs_qs = Observations.objects.filter(utc=utc, pulsar=psr, beam=beam)
    count = obs_qs.count()

    if count == 0 or update:
        if count == 0:
            obs = Observations(utc=utc, pulsar=psr, beam=beam,)
        else:
            obs = obs_qs[0]
        obs.dm_fold = DM
        obs.snr_spip = snr
        obs.length = length
        obs.nchan = nchan
        obs.nbin = nbin
        obs.nsubint = nsubint
        obs.nant = nant
        obs.nant_eff = nant_eff
        obs.proposal = proposal_obj
        obs.bw = bw
        obs.frequency = freq
        obs.ra = RA
        obs.dec = DEC
        obs.schedule = schedule
        obs.phaseup = phaseup

        plots = {}
        plots["profile"] = profile
        plots["phase_vs_time"] = phase_vs_time
        plots["phase_vs_frequency"] = phase_vs_frequency
        plots["bandpass"] = bandpass
        plots["snr_vs_time"] = snr_vs_time
        for img_type, img_b64bytes in plots.items():
            if img_b64bytes:
                # we transport images as base64 encoded bytes
                image_cf = ContentFile(b64decode(img_b64bytes))
                # obtain the matching image from observation instance:
                img_attr = getattr(obs, img_type)
                img_attr.save(f"{img_type}.png", image_cf)
        obs.save()
        msg = f"Observation with UTC: {utc} psr: {psr} beam: {beam} saved"
        logging.info(msg)

        # post to slack if this was a new obs
        if count == 0:
            url = "https://pulsars.org.au" + reverse(
                "obs_detail", kwargs={"psr": f"{psr}", "beam": f"{beam}", "utc": f"{utc}",}
            )
            msg = f"An observation of {psr}  in beam {beam} at UTC of {utc} was just added to the portal. The S/N as determined by the backend was {snr:.1f}. See more at {url}."
            post_to_slack_if_meertime(msg, proposal)

        return obs
    else:
        msg = f"Observation with UTC: {utc} psr: {psr} beam: {beam} already existed and update was not requested"
        logging.warning(msg)
        return None


def create_search_mode(
    utc,
    psr,
    beam,
    ra,
    dec,
    DM,
    nbit,
    nchan,
    npol,
    tsamp,
    nant,
    nant_eff,
    proposal,
    length,
    bw,
    freq,
    schedule=None,
    phaseup=None,
    update=False,
):
    if update == "false" or update == "False":
        update = False

    utc, psr, proposal_obj, schedule, phaseup = get_utc_psr_proposal_schedule_phaseup(
        utc, psr, proposal, schedule, phaseup
    )

    sm_qs = Searchmode.objects.filter(utc=utc, pulsar=psr, beam=beam)
    count = sm_qs.count()
    if count == 0 or update:
        if count == 0:
            sm = Searchmode(utc=utc, pulsar=psr, beam=beam,)
        else:
            sm = sm_qs[0]
        sm.ra = ra
        sm.dec = dec
        sm.dm = DM
        sm.nbit = nbit
        sm.nchan = nchan
        sm.npol = npol
        sm.tsamp = tsamp
        sm.nant = nant
        sm.nant_eff = nant_eff
        sm.proposal = proposal_obj
        sm.length = length
        sm.bw = bw
        sm.frequency = freq
        sm.schedule = schedule
        sm.phaseup = phaseup

        sm.save()
        msg = f"Searchmode with UTC: {utc} psr: {psr} beam: {beam} saved"
        logging.info(msg)

        if count == 0:
            msg = f"A searchmode observation of {psr} in beam {beam} at UTC of {utc} was just added to the portal."
            post_to_slack_if_meertime(msg, proposal)

        return sm
    else:
        msg = f"Searchmode with UTC: {utc} psr: {psr} beam: {beam} already existed and update was not requested"
        logging.warning(msg)
        return None


def create_fluxcal(
    utc, psr, beam, snr, length, nchan, nbin, nant, nant_eff, proposal, bw, freq, schedule=None, phaseup=None
):
    # get the foreign keys:
    utc, psr, proposal_obj, schedule, phaseup = get_utc_psr_proposal_schedule_phaseup(
        utc, psr, proposal, schedule, phaseup
    )

    obs_qs = Fluxcal.objects.filter(utc=utc, pulsar=psr, beam=beam)
    if obs_qs.count() == 0:
        new_obs = Fluxcal(
            utc=utc,
            pulsar=psr,
            beam=beam,
            snr_spip=snr,
            length=length,
            nchan=nchan,
            nbin=nbin,
            nant=nant,
            nant_eff=nant_eff,
            proposal=proposal_obj,
            bw=bw,
            frequency=freq,
            schedule=schedule,
            phaseup=phaseup,
        )
        new_obs.save()
        msg = f"Fluxcal with UTC: {utc} psr: {psr} beam: {beam} saved"
        logging.info(msg)
        return new_obs
    else:
        msg = f"Fluxcal with UTC: {utc} psr: {psr} beam: {beam} already existed"
        logging.warning(msg)
        return None


def parse_input(line):
    input_data = line.split()

    # legacy fold mode input:
    if len(input_data) == 14 and input_data[13] == "0":
        # raw fold mode
        utc = input_data[0]
        psr = input_data[1]
        beam = input_data[2]
        DM = input_data[3]
        snr = input_data[4]
        length = input_data[5]
        nchan = input_data[6]
        nbin = input_data[7]
        nant = input_data[8]
        nant_eff = input_data[9]
        proposal = input_data[10]
        bw = input_data[11]
        freq = input_data[12]

        # populate fields not present in legacy inputs
        profile = ""
        phase_vs_time = ""
        phase_vs_frequency = ""
        bandpass = ""
        snr_vs_time = ""
        update = "false"

        try:
            snr = float(snr)
        except ValueError:
            snr = None

        create_fold_mode(
            utc,
            psr,
            beam,
            "",
            "",
            DM,
            snr,
            length,
            nchan,
            nbin,
            -1,
            nant,
            nant_eff,
            proposal,
            bw,
            freq,
            profile,
            phase_vs_time,
            phase_vs_frequency,
            bandpass,
            snr_vs_time,
            None,
            None,
            update,
        )
    elif len(input_data) == 25 and input_data[24] == "0":
        # raw fold mode
        utc = input_data[0]
        psr = input_data[1]
        beam = input_data[2]
        RA = input_data[3]
        DEC = input_data[4]
        DM = input_data[5]
        snr = input_data[6]
        length = input_data[7]
        nchan = input_data[8]
        nbin = input_data[9]
        nsubint = input_data[10]
        nant = input_data[11]
        nant_eff = input_data[12]
        proposal = input_data[13]
        bw = input_data[14]
        freq = input_data[15]
        profile = handle_image_parsing(input_data[16])
        phase_vs_time = handle_image_parsing(input_data[17])
        phase_vs_frequency = handle_image_parsing(input_data[18])
        bandpass = handle_image_parsing(input_data[19])
        snr_vs_time = handle_image_parsing(input_data[20])
        schedule = input_data[21]
        phaseup = input_data[22]
        update = input_data[23]

        try:
            snr = float(snr)
        except ValueError:
            snr = None

        create_fold_mode(
            utc,
            psr,
            beam,
            RA,
            DEC,
            DM,
            snr,
            length,
            nchan,
            nbin,
            nsubint,
            nant,
            nant_eff,
            proposal,
            bw,
            freq,
            profile,
            phase_vs_time,
            phase_vs_frequency,
            bandpass,
            snr_vs_time,
            schedule,
            phaseup,
            update,
        )

    elif len(input_data) == 19 and input_data[18] == "1":
        # searchmode
        utc = input_data[0]
        psr = input_data[1]
        beam = input_data[2]
        ra = input_data[3]
        dec = input_data[4]
        DM = input_data[5]
        nbit = input_data[6]
        nchan = input_data[7]
        npol = input_data[8]
        tsamp = input_data[9]
        nant = input_data[10]
        nant_eff = input_data[11]
        proposal = input_data[12]
        length = input_data[13]
        bw = input_data[14]
        freq = input_data[15]
        schedule = input_data[16]
        phaseup = input_data[17]

        # in searchmode, length can be malformed:
        try:
            float(length)
        except ValueError:
            length = "-1"

        create_search_mode(
            utc,
            psr,
            beam,
            ra,
            dec,
            DM,
            nbit,
            nchan,
            npol,
            tsamp,
            nant,
            nant_eff,
            proposal,
            length,
            bw,
            freq,
            schedule,
            phaseup,
        )

    elif len(input_data) == 15 and input_data[14] == "2":
        # fluxcal
        utc = input_data[0]
        psr = input_data[1]
        beam = input_data[2]
        snr = input_data[4]
        length = input_data[5]
        nchan = input_data[6]
        nbin = input_data[7]
        nant = input_data[8]
        nant_eff = input_data[9]
        proposal = input_data[10]
        bw = input_data[11]
        freq = input_data[12]
        schedule = input_data[13]
        phaseup = input_data[14]

        create_fluxcal(utc, psr, beam, snr, length, nchan, nbin, nant, nant_eff, proposal, bw, freq, schedule, phaseup)

    elif len(input_data) == 5 and input_data[4] == "3":
        # par file
        psr = input_data[0]
        updated_at = input_data[1]
        ephemeris_fn = input_data[2]
        comment = input_data[3]

        ephemeris = json.dumps(parse_cfg(ephemeris_fn), separators=(",", ":"))

        create_ephemeris(psr, updated_at, ephemeris, comment)

    else:
        msg = f"Currently only folded, search mode, fluxcal, or ephemeris input is accepted. You either tried to insert different type or malformed the fold mode input. Input: {line}"
        logging.warning(msg)
