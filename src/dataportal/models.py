from django.db import models
from django.db.models import Max, Min, F, ExpressionWrapper, DurationField, Count, Sum, Avg, OuterRef, Subquery
from django.db.models.functions import Sqrt
from .logic import get_band


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

    @property
    def band(self):
        return get_band(self.frequency)

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

    @classmethod
    def get_table_data(cls, mode="fold", proposal_id=None):
        if mode == "search":
            return cls.project_searchmode(proposal_id) if proposal_id else cls.all_searchmode()
        return cls.project_observations(proposal_id) if proposal_id else cls.all_observations()

    @classmethod
    def all_observations(cls):
        latest_observation = Observations.objects.filter(pulsar=OuterRef("pk")).order_by("-utc__utc_ts")
        return (
            cls.objects.filter(observations__isnull=False)
            .values("jname", "pk")
            .annotate(
                last=Max("observations__utc__utc_ts"),
                first=Min("observations__utc__utc_ts"),
                proposal_short=Subquery(latest_observation.values("proposal__proposal_short")[:1]),
                timespan=ExpressionWrapper(
                    Max("observations__utc__utc_ts") - Min("observations__utc__utc_ts"), output_field=DurationField()
                ),
                nobs=Count("observations"),
                total_tint_h=Sum("observations__length") / 60 / 60,
                avg_snr_5min=Avg(F("observations__snr_pipe") / Sqrt(F("observations__length")) * Sqrt(300)),
                max_snr_5min=Max(F("observations__snr_pipe") / Sqrt(F("observations__length")) * Sqrt(300)),
                latest_snr=Subquery(latest_observation.values("snr_spip")[:1]),
                latest_tint_m=Subquery(latest_observation.values("length")[:1]) / 60,
            )
        )

    @classmethod
    def project_observations(cls, proposal_id):
        latest_observation = Observations.objects.filter(pulsar=OuterRef("pk"), proposal_id=proposal_id).order_by(
            "-utc__utc_ts"
        )
        return (
            cls.objects.filter(observations__isnull=False, observations__proposal__id=proposal_id)
            .values("jname", "pk")
            .annotate(
                last=Max("observations__utc__utc_ts"),
                first=Min("observations__utc__utc_ts"),
                proposal_short=Subquery(latest_observation.values("proposal__proposal_short")[:1]),
                timespan=ExpressionWrapper(
                    Max("observations__utc__utc_ts") - Min("observations__utc__utc_ts"), output_field=DurationField(),
                ),
                nobs=Count("observations"),
                total_tint_h=Sum("observations__length") / 60 / 60,
                avg_snr_5min=Avg(F("observations__snr_pipe") / Sqrt(F("observations__length")) * Sqrt(300)),
                max_snr_5min=Max(F("observations__snr_pipe") / Sqrt(F("observations__length")) * Sqrt(300)),
                latest_snr=Subquery(latest_observation.values("snr_spip")[:1]),
                latest_tint_m=Subquery(latest_observation.values("length")[:1]) / 60,
            )
        )

    @classmethod
    def all_searchmode(cls):
        latest_searchmode = Searchmode.objects.filter(pulsar=OuterRef("pk")).order_by("-utc__utc_ts")
        return (
            cls.objects.filter(searchmode__isnull=False)
            .values("jname", "pk")
            .annotate(
                last=Max("searchmode__utc__utc_ts"),
                first=Min("searchmode__utc__utc_ts"),
                proposal_short=Subquery(latest_searchmode.values("proposal__proposal_short")[:1]),
                timespan=ExpressionWrapper(
                    Max("searchmode__utc__utc_ts") - Min("observations__utc__utc_ts"), output_field=DurationField()
                ),
                nobs=Count("searchmode"),
                total_tint_h=Sum("searchmode__length") / 60 / 60,
            )
        )

    @classmethod
    def project_searchmode(cls, proposal_id):
        latest_searchmode = Observations.objects.filter(pulsar=OuterRef("pk"), proposal_id=proposal_id).order_by(
            "-utc__utc_ts"
        )
        return (
            cls.objects.filter(observations__proposal__id=proposal_id)
            .values("jname", "pk")
            .annotate(
                last=Max("observations__utc__utc_ts"),
                first=Min("observations__utc__utc_ts"),
                proposal_short=Subquery(latest_searchmode.values("proposal__proposal_short")[:1]),
                timespan=ExpressionWrapper(
                    Max("observations__utc__utc_ts") - Min("observations__utc__utc_ts"), output_field=DurationField(),
                ),
                nobs=Count("observations"),
                total_tint_h=Sum("observations__length") / 60 / 60,
                avg_snr_5min=Avg(F("observations__snr_pipe") / Sqrt(F("observations__length")) * Sqrt(300)),
                max_snr_5min=Max(F("observations__snr_pipe") / Sqrt(F("observations__length")) * Sqrt(300)),
                latest_snr=Subquery(latest_searchmode.values("snr_spip")[:1]),
                latest_tint_m=Subquery(latest_searchmode.values("length")[:1]) / 60,
            )
        )

    def observations_detail_data(self):
        return self.observations_set.all().order_by("-utc__utc_ts")

    def searchmode_detail_data(self):
        return self.searchmode_set.all().order_by("-utc__utc_ts")

    class Meta:
        db_table = "Pulsars"


class Searchmode(models.Model):
    pulsar = models.ForeignKey(Pulsars, models.DO_NOTHING)
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

    @property
    def band(self):
        return get_band(self.frequency)

    class Meta:
        db_table = "Searchmode"
        unique_together = (("pulsar", "utc", "beam"),)


class Fluxcal(models.Model):
    pulsar = models.ForeignKey(Pulsars, models.DO_NOTHING)
    utc = models.ForeignKey("Utcs", models.DO_NOTHING)
    proposal = models.ForeignKey(Proposals, models.DO_NOTHING, blank=True, null=True)
    beam = models.IntegerField()
    comment = models.TextField(blank=True, null=True, default=None)
    length = models.FloatField(blank=True, null=True)
    bw = models.FloatField()
    frequency = models.FloatField()
    nchan = models.IntegerField()
    nbin = models.IntegerField()
    nant = models.IntegerField()
    nant_eff = models.IntegerField()
    snr_spip = models.FloatField(blank=True, null=True)

    @property
    def band(self):
        return get_band(self.frequency)

    class Meta:
        db_table = "Fluxcal"
        unique_together = (("pulsar", "utc", "beam"),)


class Utcs(models.Model):
    utc = models.TextField(blank=True, null=True)
    utc_ts = models.DateTimeField()
    annotation = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "UTCs"
