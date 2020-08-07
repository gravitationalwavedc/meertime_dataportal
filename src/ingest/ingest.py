from datetime import datetime
import sys
import os
import logging


def __setup_django(root_path, settings):
    import django

    os.chdir(root_path)

    # Django settings
    sys.path.append(root_path)
    os.environ["DJANGO_SETTINGS_MODULE"] = settings

    django.setup()


__setup_django(os.environ.get("PWD", "."), "meertime.settings")

from dataportal.models import Observations, Searchmode, Utcs, Pulsars, Proposals


def parse_input(line):
    input_data = line.split()
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

        # get the foreign keys:
        utc_dt = datetime.strptime(input_data[0], "%Y-%m-%d-%H:%M:%S")  # WARNING: naive dt
        utc, created = Utcs.objects.get_or_create(utc=input_data[0], utc_ts=utc_dt)
        psr, created = Pulsars.objects.get_or_create(jname=psr)
        proposal, created = Proposals.objects.get_or_create(proposal=proposal)

        obs_qs = Observations.objects.filter(utc=utc, pulsar=psr, beam=beam)
        if obs_qs.count() == 0:
            new_obs = Observations(
                utc=utc,
                pulsar=psr,
                beam=beam,
                dm_fold=DM,
                snr_spip=snr,
                length=length,
                nchan=nchan,
                nbin=nbin,
                nant=nant,
                nant_eff=nant_eff,
                proposal=proposal,
                bw=bw,
                frequency=freq,
            )
            new_obs.save()
            msg = f"Observation with UTC: {utc} psr: {psr} beam: {beam} saved"
            logging.info(msg)
        else:
            msg = f"Observation with UTC: {utc} psr: {psr} beam: {beam} already existed"
            logging.warning(msg)

    elif len(input_data) == 17 and input_data[16] == "1":
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

        # in searchmode, length can be malformed:
        try:
            float(length)
        except ValueError:
            length = "-1"

        utc_dt = datetime.strptime(input_data[0], "%Y-%m-%d-%H:%M:%S")  # WARNING: naive dt
        utc, created = Utcs.objects.get_or_create(utc=input_data[0], utc_ts=utc_dt)
        psr, created = Pulsars.objects.get_or_create(jname=psr)
        proposal, created = Proposals.objects.get_or_create(proposal=proposal)

        sm_qs = Searchmode.objects.filter(utc=utc, pulsar=psr, beam=beam)
        if sm_qs.count() == 0:
            new_sm = Searchmode(
                utc=utc,
                pulsar=psr,
                beam=beam,
                ra=ra,
                dec=dec,
                dm=DM,
                nbit=nbit,
                nchan=nchan,
                npol=npol,
                tsamp=tsamp,
                nant=nant,
                nant_eff=nant_eff,
                proposal=proposal,
                length=length,
                bw=bw,
                frequency=freq,
            )
            new_sm.save()
            msg = f"Searchmode with UTC: {utc} psr: {psr} beam: {beam} saved"
            logging.info(msg)
        else:
            msg = f"Searchmode with UTC: {utc} psr: {psr} beam: {beam} already existed"
            logging.warning(msg)
    else:
        msg = "Currently only fold mode input is accepted. You either tried to insert different type or malformed the fold mode input."
        logging.warning(msg)


if __name__ == "__main__":
    input_fn = "ingest/example.input"
    with open(input_fn, "r") as input_fh:
        for line in input_fh:
            parse_input(line)
