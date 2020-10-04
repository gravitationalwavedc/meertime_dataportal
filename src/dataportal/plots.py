from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool, LinearInterpolator
from bokeh.embed import components


def pulsar_summary_plot(UTCs, SNRs, lengths, height=300, width=800):
    """
    This function generates a pulsar summary plot in bokeh.
    The summary plot shows S/N vs time with size of the point proportional to integration time / length.

    Inputs are lists and have to be equal length.
    UTCs must be datetimes
    SNRs and lengths must be floats

    returns a javascript and a div as strings for embedding in webpages
    """
    if len(UTCs) != len(SNRs) or len(UTCs) != len(lengths) or len(UTCs) == 0:
        return "<script></script>", "<div></div>"
    TOOLS = "box_zoom, reset, box_select, hover"
    fig = figure(
        plot_height=height,
        plot_width=width,
        tools=TOOLS,
        toolbar_location="right",
        x_axis_type="datetime",
        y_axis_type="log",
        x_axis_label="UTC",
        y_axis_label="S/N",
        title="Point size indicates integration time",
    )
    fig.background_fill_color = "#fafafa"
    fig.border_fill_color = "#fafafa"

    # configure the tooltip:
    hover = fig.select(dict(type=HoverTool))
    hover.tooltips = [("raw S/N", "@snr{%0.1f}"), ("integration time [s]", "@length{%0.1f}"), ("UTC", "@UTC{%F %T}")]
    hover.formatters = {"@UTC": "datetime", "@snr": "printf", "@length": "printf"}

    # set up a data source:
    source = ColumnDataSource(data=dict(UTC=UTCs, length=lengths, snr=SNRs))

    # interpolate integration times for use as point size
    size_mapper = LinearInterpolator(x=[min(lengths), max(lengths)], y=[5, 50])

    plot = fig.circle(x="UTC", y="snr", source=source, size={"field": "length", "transform": size_mapper}, alpha=0.5,)

    script, div = components(fig)
    return script, div
