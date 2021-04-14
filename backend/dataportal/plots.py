from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, LinearInterpolator
from bokeh.embed import components
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models.tickers import DatetimeTicker
from bokeh.transform import factor_mark
from datetime import timedelta
from numpy import sqrt, log10, power


def get_interpolator(
    values, min_point_size=sqrt(60.0), max_point_size=60.0, min_value=sqrt(60.0), max_value=sqrt(3600.0)
):
    """
    Interpolate point size as equal to the sqrt of integration time / length.
    If values are within the expected range (1 minute to 1 hour by default), use the sqrt(length)
    If the values extend beyond the expected range on either end, clip to the expected range to avoid point sizes growing beyond max_point_size.
    However, do not clip points on the plot, merely restrict them to the maximum point size.
    """

    if max(values) < max_value:
        max_point_size = max(values)
        max_value = max(values)
    if min(values) > min_value:
        min_point_size = min(values)
        min_value = min(values)

    interpolator = LinearInterpolator(x=[min_value, max_value], y=[min_point_size, max_point_size], clip=False)
    return interpolator


def pulsar_summary_plot(UTCs, SNRs, lengths, bands, height=300, width=800, sizing_mode="scale_both"):
    """
    This function generates a pulsar summary plot in bokeh.
    The summary plot shows S/N vs time with size of the point proportional to integration time / length.

    Inputs are lists or tuples and have to be equal length.
    UTCs must be datetimes
    SNRs and lengths must be floats

    returns a javascript and a div as strings for embedding in webpages
    """
    if len(UTCs) != len(SNRs) or len(UTCs) != len(lengths) or len(UTCs) == 0:
        return "<script></script>", "<div></div>"
    TOOLS = "box_zoom, reset, hover, save"
    FIGURE_OPTIONS = dict(
        plot_height=height,
        plot_width=width,
        sizing_mode=sizing_mode,
        toolbar_location="right",
        x_axis_type="datetime",
        y_axis_type="log",
        x_axis_label="UTC",
        y_axis_label="S/N",
        title="Point size indicates integration time. Point shape indicates observing band.",
    )

    fig = figure(tools=TOOLS, **FIGURE_OPTIONS,)

    # increase font size on labels
    fig.xaxis.axis_label_text_font_size = "16pt"
    fig.yaxis.axis_label_text_font_size = "16pt"
    fig.yaxis.major_label_text_font_size = "12pt"
    fig.xaxis.major_label_text_font_size = "12pt"
    fig.background_fill_color = "#fafafa"
    fig.border_fill_color = "#fafafa"

    sqrt_lengths = sqrt(lengths)

    # configure the tooltip:
    hover = fig.select(dict(type=HoverTool))
    hover.tooltips = [
        ("raw S/N", "@snr{%0.1f}"),
        ("integration time [s]", "@length{%0.1f}"),
        ("UTC", "@UTC{%F %T}"),
        ("band", "@bands"),
    ]
    hover.formatters = {"@UTC": "datetime", "@snr": "printf", "@length": "printf"}

    # set up a data source:
    source = ColumnDataSource(data=dict(UTC=UTCs, length=lengths, snr=SNRs, sqrt_length=sqrt_lengths, bands=bands))

    symbol_mapper = factor_mark(
        "bands", factors=["L-band", "UHF", "S-band", "Unknown"], markers=["circle", "square", "diamond", "triangle"],
    )

    plot = fig.scatter(
        x="UTC",
        y="snr",
        source=source,
        size={"field": "sqrt_length", "transform": get_interpolator(sqrt_lengths)},
        marker=symbol_mapper,
        fill_alpha=0.5,
    )

    # Plots should default to at least a week of range to avoid pointless units like anything between us and h.
    # while still providing a reasonable default if the only observation of a source are on a single day.
    fig.xaxis.formatter = DatetimeTickFormatter(days="%d/%m/%Y", months="%m/%Y", years="%Y")

    # We'd like to ensure the y-range includes complete points at their maximum size. However, we do not know how big
    # the plot will be and thus cannot determine how many dex do 60 pixels (default max point size) correspond to.
    # We assume that 0.2 dex will be enough. This should be a decent compromise between including pulsar like J0437
    # with very large S/N in long observations as well as more regular pulsars where 0.2 dex is a bit more than we'd
    # like.
    # We only do this if there's more than one point, otherwise the 0.2 dex padding produces essentially an empty plot
    if len(SNRs) > 1:
        fig.y_range.end = power(10, log10(max(SNRs)) + 0.2)

    script, div = components(fig)
    return script, div
