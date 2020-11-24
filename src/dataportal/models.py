from django.db import models


class Basebandings(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)


class Caspsrconfigs(models.Model):
    observation = models.ForeignKey("Observations", models.DO_NOTHING)
    pid = models.CharField(max_length=16)
    configuration = models.TextField()  # This field type is a guess.


class Collections(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True, null=True)


class Ephemerides(models.Model):
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    ephemeris = models.TextField()  # This field type is a guess.
    p0 = models.DecimalField(max_digits=10, decimal_places=8)
    dm = models.FloatField()
    rm = models.FloatField()
    comment = models.CharField(max_length=255, blank=True, null=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()


class Filterbankings(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    nbit = models.IntegerField()
    npol = models.IntegerField()
    nchan = models.IntegerField()
    tsamp = models.FloatField()
    dm = models.FloatField()


class Foldings(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    folding_ephemeris = models.ForeignKey(Ephemerides, models.DO_NOTHING)
    nbin = models.IntegerField()
    npol = models.IntegerField()
    nchan = models.IntegerField()
    dm = models.FloatField(blank=True, null=True)
    tsubint = models.IntegerField()


class Instrumentconfigs(models.Model):
    bandwidth = models.DecimalField(max_digits=12, decimal_places=6)
    frequency = models.DecimalField(max_digits=15, decimal_places=9)
    nchan = models.IntegerField()
    npol = models.IntegerField()
    beam = models.CharField(max_length=16)


class Launches(models.Model):
    pipeline = models.ForeignKey("Pipelines", models.DO_NOTHING)
    parent_pipeline = models.ForeignKey("Pipelines", models.DO_NOTHING, blank=True, null=True)
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)


class Observations(models.Model):
    target = models.ForeignKey("Targets", models.DO_NOTHING)
    utc_start = models.DateTimeField()
    duration = models.FloatField()
    obs_type = models.CharField(max_length=8)
    telescope = models.ForeignKey("Telescopes", models.DO_NOTHING)
    instrument_config = models.ForeignKey(Instrumentconfigs, models.DO_NOTHING)
    suspect = models.IntegerField()
    comment = models.CharField(max_length=255, blank=True, null=True)


class Ptusecalibrations(models.Model):
    calibration_type = models.CharField(max_length=4)
    location = models.CharField(max_length=255, blank=True, null=True)


class Ptuseconfigs(models.Model):
    observation = models.ForeignKey(Observations, models.DO_NOTHING)
    calibration = models.ForeignKey(Ptusecalibrations, models.DO_NOTHING)
    proposal_id = models.CharField(max_length=32)
    schedule_block_id = models.CharField(max_length=32)
    experiment_id = models.CharField(max_length=32)
    phaseup_id = models.CharField(max_length=32, blank=True, null=True)
    delaycal_id = models.CharField(max_length=32, blank=True, null=True)
    nant = models.IntegerField()
    nant_eff = models.IntegerField()
    configuration = models.TextField()  # This field type is a guess.


class Pipelineimages(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    rank = models.IntegerField()
    image_type = models.CharField(max_length=64, blank=True, null=True)
    image = models.CharField(max_length=255)


class Pipelines(models.Model):
    name = models.CharField(max_length=64)
    description = models.CharField(max_length=255, blank=True, null=True)
    revision = models.CharField(max_length=16)
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    configuration = models.TextField(blank=True, null=True)  # This field type is a guess.


class Processingcollections(models.Model):
    processing = models.ForeignKey("Processings", models.DO_NOTHING)
    collection = models.ForeignKey(Collections, models.DO_NOTHING)


class Processings(models.Model):
    observation = models.ForeignKey(Observations, models.DO_NOTHING)
    pipeline = models.ForeignKey(Pipelines, models.DO_NOTHING)
    parent = models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)
    location = models.CharField(max_length=255)
    job_state = models.CharField(max_length=255, blank=True, null=True)
    job_output = models.TextField(blank=True, null=True)  # This field type is a guess.
    results = models.TextField(blank=True, null=True)  # This field type is a guess.


class Pulsaraliases(models.Model):
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    alias = models.CharField(max_length=64)


class Pulsartargets(models.Model):
    target = models.ForeignKey("Targets", models.DO_NOTHING)
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)


class Pulsars(models.Model):
    jname = models.CharField(max_length=64)
    state = models.CharField(max_length=255, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)


class Rfis(models.Model):
    processing = models.ForeignKey(Processings, models.DO_NOTHING)
    folding = models.ForeignKey(Foldings, models.DO_NOTHING)
    percent_zapped = models.FloatField()


class Targets(models.Model):
    name = models.CharField(max_length=64)
    raj = models.CharField(max_length=16)
    decj = models.CharField(max_length=16)


class Telescopes(models.Model):
    name = models.CharField(max_length=64)


class Templates(models.Model):
    pulsar = models.ForeignKey(Pulsars, models.DO_NOTHING)
    frequency = models.FloatField()
    bandwidth = models.FloatField()
    created_at = models.DateTimeField()
    created_by = models.CharField(max_length=64)
    location = models.CharField(max_length=255)
    method = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)


class Toas(models.Model):
    processing = models.ForeignKey(Processings, models.DO_NOTHING)
    input_folding = models.ForeignKey(Foldings, models.DO_NOTHING)
    timing_ephemeris = models.ForeignKey(Ephemerides, models.DO_NOTHING, blank=True, null=True)
    template = models.ForeignKey(Templates, models.DO_NOTHING)
    flags = models.TextField()  # This field type is a guess.
    frequency = models.FloatField()
    mjd = models.CharField(max_length=32, blank=True, null=True)
    site = models.IntegerField(blank=True, null=True)
    uncertainty = models.FloatField(blank=True, null=True)
    valid = models.IntegerField(blank=True, null=True)
    comment = models.CharField(max_length=255, blank=True, null=True)
