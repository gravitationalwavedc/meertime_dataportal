import { Spinner } from "react-bootstrap";
import Plot from "react-plotly.js";

const PlotLoading = () => {
  return (
    <>
      <Spinner
        animation="border"
        role="status"
        className="plot-spinner text-primary-600"
      >
        <span className="sr-only">Loading Timing Residuals Plot...</span>
      </Spinner>
      <Plot
        data={[]}
        layout={{
          title: "Loading...",
          autosize: true,
          margin: {
            t: 40,
            r: 40,
            b: 60,
            l: 60,
          },
          paper_bgcolor: "rgba(1, 1, 1, 0)",
          plot_bgcolor: "rgba(1, 1, 1, 0)",
          legend: { orientation: "h" },
        }}
        useResizeHandler={true}
        style={{ width: "100%", height: "100%" }}
        config={{
          displaylogo: false,
          displayModeBar: true,
          modeBarButtonsToRemove: ["resetScale2d"],
        }}
      />
    </>
  );
};

export default PlotLoading;
