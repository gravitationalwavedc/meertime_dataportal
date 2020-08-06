from django.db import models


class Observations(models.Model):
    pulsar = models.ForeignKey("Pulsars", models.DO_NOTHING)
    utc = models.ForeignKey("Utcs", models.DO_NOTHING)
    proposal = models.ForeignKey("Proposals", models.DO_NOTHING, blank=True, null=True)
    beam = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    bw = models.FloatField(blank=True, null=True)
    frequency = models.FloatField(blank=True, null=True)
    rm_pipe = models.FloatField(db_column="RM_pipe", blank=True, null=True)
    dm_pipe = models.FloatField(db_column="DM_pipe", blank=True, null=True)
    dm_fold = models.FloatField(db_column="DM_fold", blank=True, null=True)
    nchan = models.IntegerField(blank=True, null=True)
    nbin = models.IntegerField(blank=True, null=True)
    mjd = models.TextField(db_column="MJD", blank=True, null=True)
    mjd_int = models.IntegerField(db_column="MJD_INT", blank=True, null=True)
    mjd_frac = models.TextField(db_column="MJD_frac", blank=True, null=True)
    pa = models.FloatField(db_column="PA", blank=True, null=True)
    ra = models.TextField(db_column="RA", blank=True, null=True)
    dec = models.TextField(db_column="DEC", blank=True, null=True)
    observer = models.TextField(blank=True, null=True)
    snr_pipe = models.FloatField(db_column="SNR_pipe", blank=True, null=True)
    snr_spip = models.FloatField(db_column="SNR_spip", blank=True, null=True)
    nant = models.IntegerField(blank=True, null=True)
    nant_eff = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "Observations"
        unique_together = (("pulsar", "utc", "beam"),)


class Proposals(models.Model):
    proposal = models.TextField(blank=True, null=True)
    proposal_short = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "Proposals"


class Pulsars(models.Model):
    jname = models.TextField(db_column="Jname", blank=True, null=True)
    state = models.TextField(blank=True, null=True)
    gc = models.IntegerField(db_column="GC", blank=True, null=True)
    relbin = models.IntegerField(db_column="RelBin", blank=True, null=True)
    tpa = models.IntegerField(db_column="TPA", blank=True, null=True)
    pta = models.IntegerField(db_column="PTA", blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "Pulsars"


class Searchmode(models.Model):
    pulsar = models.ForeignKey(Pulsars, models.DO_NOTHING, primary_key=True)
    utc = models.ForeignKey("Utcs", models.DO_NOTHING)
    proposal = models.ForeignKey(Proposals, models.DO_NOTHING, blank=True, null=True)
    beam = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    tsamp = models.FloatField(blank=True, null=True)
    bw = models.FloatField(blank=True, null=True)
    frequency = models.FloatField(blank=True, null=True)
    nchan = models.IntegerField(blank=True, null=True)
    nbit = models.IntegerField(blank=True, null=True)
    npol = models.IntegerField(blank=True, null=True)
    nant = models.IntegerField(blank=True, null=True)
    nant_eff = models.IntegerField(blank=True, null=True)
    dm = models.FloatField(db_column="DM", blank=True, null=True)
    ra = models.TextField(db_column="RA", blank=True, null=True)
    dec = models.TextField(db_column="DEC", blank=True, null=True)

    class Meta:
        db_table = "Searchmode"
        unique_together = (("pulsar", "utc", "beam"),)


class Utcs(models.Model):
    utc = models.TextField(blank=True, null=True)
    utc_ts = models.DateTimeField()
    annotation = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "UTCs"
