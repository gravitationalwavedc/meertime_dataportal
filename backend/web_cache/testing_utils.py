from datetime import datetime

from dataportal.models import (
    Pulsars,
    Targets,
    Telescopes,
    Programs,
    Projects,
    Instrumentconfigs,
    Observations,
    Pipelines,
    Processings,
    Ephemerides,
    Pulsartargets,
    Foldings,
    Filterbankings,
    Pipelineimages,
)


def create_folding_for_molonglo():
    jname = "J0125-2327"

    pulsar = Pulsars.objects.create(jname=jname)

    target = Targets.objects.create(name="J0125-2327", raj="1:25:01.06", decj="-23:27:08.2")

    telescope = Telescopes.objects.create(name="my first telescope")

    program = Programs.objects.create(name="MeerTime", telescope=telescope)

    project = Projects.objects.create(code="SCI_thinga_MB", short="RelBin", program=program)

    instrument_config = Instrumentconfigs.objects.create(
        name="my config", bandwidth=11, frequency=839, nchan=42, npol=44, beam=54
    )

    observation = Observations.objects.create(
        target=target,
        telescope=telescope,
        project=project,
        instrument_config=instrument_config,
        utc_start=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        duration=21,
    )

    observation = Observations.objects.create(
        target=target,
        telescope=telescope,
        project=project,
        instrument_config=instrument_config,
        utc_start=datetime.strptime("2000-01-21-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        duration=4,
    )

    pipeline = Pipelines.objects.create(
        name="ye pipeline",
        revision=1,
        created_at=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        created_by="Buffy Summers",
    )

    relbin_pipeline = Pipelines.objects.create(
        name="MONSPSR_CLEAN",
        revision=1,
        created_at=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        created_by="Buffy Summers",
    )

    processing = Processings.objects.create(
        observation=observation,
        pipeline=pipeline,
        embargo_end=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        location="me",
        results={"snr": 67.800, "flux": 1.46},
    )

    # Create a parent processing for the sn_meerpipe
    Processings.objects.create(
        observation=observation,
        parent=processing,
        pipeline=relbin_pipeline,
        embargo_end=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        location="me",
        results={"snr": 42.1, "flux": 1.22},
    )

    ephemerides = Ephemerides.objects.create(
        pulsar=pulsar,
        ephemeris={},
        created_at=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        created_by="Buffy Summers",
        p0=12,
        dm=24,
        rm=25,
        valid_from=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        valid_to=datetime.strptime("2000-01-03-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
    )

    Pulsartargets.objects.create(target=target, pulsar=pulsar)

    folding = Foldings.objects.create(
        processing=processing, folding_ephemeris=ephemerides, nbin=43, npol=42, nchan=21, tsubint=12.2
    )

    filter_bankings = Filterbankings.objects.create(processing=processing, nbit=1, npol=2, nchan=3, tsamp=1.2, dm=2.1)

    Pipelineimages.objects.create(processing=processing, rank=1)

    pulsar.save()
    folding.save()
    filter_bankings.save()

    return folding


def create_pulsar_with_observations():
    jname = "J0125-2327"

    pulsar = Pulsars.objects.create(jname=jname)

    target = Targets.objects.create(name="J0125-2327", raj="1:25:01.06", decj="-23:27:08.2")

    telescope = Telescopes.objects.create(name="my first telescope")

    program = Programs.objects.create(name="MeerTime", telescope=telescope)

    project = Projects.objects.create(code="SCI_thinga_MB", short="RelBin", program=program)

    instrument_config = Instrumentconfigs.objects.create(
        name="my config", bandwidth=11, frequency=839, nchan=42, npol=44, beam=54
    )

    observation = Observations.objects.create(
        target=target,
        telescope=telescope,
        project=project,
        instrument_config=instrument_config,
        utc_start=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        duration=21,
    )

    observation = Observations.objects.create(
        target=target,
        telescope=telescope,
        project=project,
        instrument_config=instrument_config,
        utc_start=datetime.strptime("2000-01-21-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        duration=4,
    )

    pipeline = Pipelines.objects.create(
        name="ye pipeline",
        revision=1,
        created_at=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        created_by="Buffy Summers",
    )

    relbin_pipeline = Pipelines.objects.create(
        name="MeerPIPE_RelBin",
        revision=1,
        created_at=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        created_by="Buffy Summers",
    )

    processing = Processings.objects.create(
        observation=observation,
        pipeline=pipeline,
        embargo_end=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        location="me",
        results={"snr": 67.800, "flux": 1.46},
    )

    # Create a parent processing for the sn_meerpipe
    Processings.objects.create(
        observation=observation,
        parent=processing,
        pipeline=relbin_pipeline,
        embargo_end=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        location="me",
        results={"snr": 42.1, "flux": 1.22},
    )

    ephemerides = Ephemerides.objects.create(
        pulsar=pulsar,
        ephemeris={},
        created_at=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        created_by="Buffy Summers",
        p0=12,
        dm=24,
        rm=25,
        valid_from=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        valid_to=datetime.strptime("2000-01-03-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
    )

    Pulsartargets.objects.create(target=target, pulsar=pulsar)

    folding = Foldings.objects.create(
        processing=processing, folding_ephemeris=ephemerides, nbin=43, npol=42, nchan=21, tsubint=12.2
    )

    filter_bankings = Filterbankings.objects.create(processing=processing, nbit=1, npol=2, nchan=3, tsamp=1.2, dm=2.1)

    Pipelineimages.objects.create(processing=processing, rank=1)

    pulsar.save()
    folding.save()
    filter_bankings.save()

    return pulsar.jname