from datetime import datetime
import pytest
from web_cache.management.commands import _command_functions as commands
from web_cache.models import FoldPulsar, FoldPulsarDetail, SearchmodePulsar, SearchmodePulsarDetail, \
    SessionPulsar, SessionDisplay
from dataportal.models import (
    Pulsars,
    Processings,
    Observations,
    Telescopes,
    Projects,
    Programs,
    Instrumentconfigs,
    Pipelines,
    Pipelineimages,
    Ephemerides,
    Foldings,
    Targets,
    Pulsartargets,
    Filterbankings,
    Sessions
)

def create_dataportal_objects():
    jname = "J0125-2327"

    pulsar = Pulsars.objects.create(jname=jname)

    target = Targets.objects.create(name='J0125-2327', raj='1:25:01.06', decj='-23:27:08.2')

    telescope = Telescopes.objects.create(name='my first telescope')

    program = Programs.objects.create(name="MeerTime", telescope=telescope)

    project = Projects.objects.create(code='SCI_thinga_MB', short='RelBin', program=program)

    instrument_config = Instrumentconfigs.objects.create(
        name='my config', bandwidth=11, frequency=839, nchan=42, npol=44, beam=54
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
        instrument_config=instrument_config, utc_start=datetime.strptime("2000-01-21-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"), duration=4,)

    pipeline = Pipelines.objects.create(
        name='ye pipeline',
        revision=1,
        created_at=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        created_by="Buffy Summers",
    )

    relbin_pipeline = Pipelines.objects.create(
        name='MeerPIPE_RelBin',
        revision=1,
        created_at=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        created_by="Buffy Summers",
    )

    processing = Processings.objects.create(
        observation=observation,
        pipeline=pipeline,
        embargo_end=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        location="me",
        results={'snr': 67.800, 'flux': 1.46},
    )

    # Create a parent processing for the sn_meerpipe
    Processings.objects.create(
        observation=observation,
        parent=processing,
        pipeline=relbin_pipeline,
        embargo_end=datetime.strptime("2000-01-01-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        location="me",
        results={'snr': 42.1, 'flux': 1.22},
    )

    ephemerides = Ephemerides.objects.create(
        pulsar=pulsar,
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

    Sessions.objects.create(
        telescope=telescope, 
        start=datetime.strptime("1996-01-01-1:00:00 +0000", "%Y-%m-%d-%H:%M:%S %z"),
        end=datetime.strptime("2060-01-04-12:59:12 +0000", "%Y-%m-%d-%H:%M:%S %z")
    )

    return folding, ephemerides, filter_bankings

@pytest.mark.django_db
def test_sync_foldmode():
    create_dataportal_objects()
    commands.sync_foldmode()
    assert FoldPulsar.objects.exists()
    assert FoldPulsarDetail.objects.exists()

@pytest.mark.django_db
@pytest.mark.enable_signals
def test_sync_foldmode_no_ephemeris():
    _, ephemerides, _ = create_dataportal_objects()
    ephemerides.pulsar = Pulsars.objects.create(jname="x22")
    ephemerides.save()
    commands.sync_foldmode()
    assert FoldPulsar.objects.count() == 2
    assert FoldPulsarDetail.objects.count() == 2
    
@pytest.mark.django_db
def test_sync_searchmode():
    create_dataportal_objects()
    commands.sync_searchmode()
    assert SearchmodePulsar.objects.exists()
    assert SearchmodePulsarDetail.objects.exists()

@pytest.mark.django_db
def test_sync_searchmode_no_target():
    _, _, filter_bankings = create_dataportal_objects()
    filter_bankings.processing.observation.target = Targets.objects.create(name='x22', raj='0', decj='0')
    filter_bankings.save()
    commands.sync_searchmode()
    print(SearchmodePulsar.objects.count(), SearchmodePulsarDetail.objects.count())
    assert SearchmodePulsar.objects.count() == 1
    assert SearchmodePulsarDetail.objects.count() == 1

@pytest.mark.django_db
@pytest.mark.enable_signals
def test_sync_sessions():
    create_dataportal_objects()
    commands.sync_sessions()
    assert SessionDisplay.objects.exists()
    assert SessionPulsar.objects.exists()
