import Plot from "react-plotly.js";
import { useRouter } from "found";
import {
  filterBandData,
  getPlotlyData,
  getXaxisFormatter,
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
  const plotlyData = getPlotlyData(plotData, xAxis, activePlot);

  return (
    <>
      <Plot
        data={plotlyData}
        layout={{
          title: activePlot,
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
          legend: { orientation: "h" },
        }}
        useResizeHandler={true}
        style={{ width: "100%", height: "100%" }}
        onClick={handlePlotClick}
        config={{
          displaylogo: false,
          displayModeBar: true,
          modeBarButtonsToRemove: ["resetScale2d"],
        }}
      />
    </>
  );
};

export default PlotlyPlot;
