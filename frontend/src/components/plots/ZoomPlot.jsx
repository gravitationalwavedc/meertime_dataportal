import React from "react";
import Plot from 'react-plotly.js';
import { useRouter } from "found";
import {
  filterBandData,
  formatYAxisTick,
  getXaxisFormatter,
  getXaxisLabel,
  getYaxisDomain,
  getYaxisLabel,
  getYaxisTicks,
  getZRange,
  toolTipFormatter,
} from "./plotData";
import _default from "react-bootstrap/esm/CardColumns";

const ZoomPlot = ({
  data,
  xAxis,
  activePlot,
  zoomArea,
  axisMin,
  axisMax,
}) => {
  const { router } = useRouter();
  const handlePlotClick = (event) => {
    // Assuming you have a link associated with each data point
    const eventID = event.points[0].data.id[0];
    const dataPoint = linkIds.find((point) => point.id === eventID);
    if (dataPoint) {
      router.push(dataPoint.link);
    }
  };

  const { plotData, minValue, maxValue, medianValue, ticks } = filterBandData(
    data,
    zoomArea
  );

  const linkIdBands = plotData.reduce((data, dataBand) => {
    // Run for each pipelineRun
    console.log("dataBand", dataBand);
    const pointLinkId = dataBand.data.reduce((result, point) => {
      console.log("point", point);
      result.push({
        id: point.id,
        link: point.link,
      });
      return result;
      },
      []
    );
    data.push(pointLinkId);
    return data;
  }, []);
  const linkIds = [].concat(...linkIdBands);

  const plotlyData = plotData.reduce((data, dataBand) => {
    console.log(Math.max(dataBand.data.map((point) => point.size)));
    const sizes = dataBand.data.map((point) => point.size);

    // Set size scale from max size
    let sizeScale;
    if (sizes.length > 0) {
      const max = Math.max(...sizes);
      console.log('Maximum size:', max);
      sizeScale = max / 30;
    } else {
      console.log('The sizes array is empty.');
      sizeScale = 1;
    }
    // Set x data
    let xData;
    if ( xAxis === "utc" ) {
      xData = dataBand.data.map((point) => point.utc);
    } else if ( xAxis === "day" ) {
      xData = dataBand.data.map((point) => point.day);
    } else if ( xAxis === "phase" ) {
      xData = dataBand.data.map((point) => point.phase);
    } else {
      xData = dataBand.data.utc;
    }
    const row = {
      id: dataBand.data.map((point) => point.id),
      x: xData,
      error_y: {
        array: dataBand.data.map((point) => point.error),
      },
      y: xData = dataBand.data.map((point) => point.value),
      customdata: dataBand.data.map((point) => point.size),
      type: "scatter",
      mode: "markers",
      name: dataBand.name,
      hovertemplate: `${getXaxisLabel(xAxis)}: %{x}<br>${getYaxisLabel(activePlot)}: %{y}<br>Integration Time (s): %{customdata}<extra></extra>`,
      marker: {
        color: dataBand.colour,
        symbol: dataBand.shape,
        size: dataBand.data.map((point) => point.size),
        sizeref: sizeScale,
        sizemin: 5,
      },
    };
    return [...data, { ...row }];
  }, []);
  console.log(plotlyData);

  return (
    <>
      <Plot
        data={plotlyData}
        layout={{
          width: 1625,
          height: 480,
          margin: {
            t: 40,
            r: 40,
            b: 60,
            l: 60,
          },
          paper_bgcolor: 'rgba(1, 1, 1, 0)',
          plot_bgcolor: 'rgba(1, 1, 1, 0)',
          xaxis: getXaxisFormatter(xAxis),
          yaxis: {
            title: {
              text: getYaxisLabel(activePlot),
            },
          },
        }}
        onClick={handlePlotClick}
      />
    </>
  );
};

export default ZoomPlot;
