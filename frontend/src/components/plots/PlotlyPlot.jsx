import Plot from "react-plotly.js";
import { useRouter } from "found";
import {
  filterBandData,
  getXaxisFormatter,
  getXaxisLabel,
  getYaxisLabel,
} from "./plotData";

const PlotlyPlot = ({ data, xAxis, activePlot }) => {
  const { router } = useRouter();

  const handlePlotClick = (plotData) => {
    const link = plotData.points[0].customdata[1];
    if (link !== "" && link !== undefined) {
      router.push(link);
    }
  };

  const { plotData } = filterBandData(data);

  // Convert data into Plotly format based on x and y axis
  const plotlyData = plotData.reduce((data, dataBand) => {
    const sizes = dataBand.data.map((point) => point.size);

    // Set size scale from max size
    let sizeScale;
    if (sizes.length > 0) {
      const max = Math.max(...sizes);
      sizeScale = max / 30;
    } else {
      sizeScale = 1;
    }
    // Set x data
    let xData;

    if (xAxis === "utc") {
      xData = dataBand.data.map((point) => point.utc);
    } else if (xAxis === "day") {
      xData = dataBand.data.map((point) => point.day);
    } else if (xAxis === "phase") {
      xData = dataBand.data.map((point) => point.phase);
    } else {
      xData = dataBand.data.utc;
    }

    const row = {
      id: dataBand.data.map((point) => point.id),
      x: xData,
      error_y: {
        array: dataBand.data.map((point) => point.error),
        width: 6,
      },
      y: (xData = dataBand.data.map((point) => point.value)),
      link: dataBand.data.map((point) => point.link),
      customdata: dataBand.data.map((point) => [point.size, point.link]),
      type: "scatter",
      mode: "markers",
      name: dataBand.name,
      hovertemplate: `${getXaxisLabel(xAxis)}: %{x${
        xAxis === "utc" ? "|%Y-%m-%d %H:%M:%S.%f" : ""
      }}<br>${getYaxisLabel(
        activePlot
      )}: %{y}<br>Integration Time (s): %{customdata[0]}<extra></extra>`,
      marker: {
        color: dataBand.colour,
        symbol: dataBand.shape,
        size: dataBand.data.map((point) => point.size),
        sizeref: sizeScale,
        sizemin: 3,
      },
    };
    return [...data, { ...row }];
  }, []);

  return (
    <>
      <Plot
        data={plotlyData}
        layout={{
          autosize: true,
          margin: {
            t: 40,
            r: 40,
            b: 60,
            l: 60,
          },
          paper_bgcolor: "rgba(1, 1, 1, 0)",
          plot_bgcolor: "rgba(1, 1, 1, 0)",
          xaxis: getXaxisFormatter(xAxis),
          yaxis: {
            title: {
              text: getYaxisLabel(activePlot),
            },
          },
        }}
        useResizeHandler={true}
        style={{ width: "100%", height: "100%" }}
        onClick={handlePlotClick}
      />
    </>
  );
};

export default PlotlyPlot;
