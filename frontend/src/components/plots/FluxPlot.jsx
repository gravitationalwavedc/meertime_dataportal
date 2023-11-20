import {
  CartesianGrid,
  Label,
  YAxis,
  ZAxis,
} from "recharts";
import React from "react";
import ScatterPlot from "./ScatterPlot";
import { fluxPlotData } from "./plotData";

const FluxPlot = ({ data, columns, search, maxPlotLength, xAxis }) => {
  const { plotData, minValue, maxValue, ticks } = fluxPlotData(
    data,
    columns,
    search,
    maxPlotLength
  );


  return (
    <ScatterPlot data={plotData} xAxis={xAxis} ticks={ticks}>
      <CartesianGrid />
      <YAxis
        type="number"
        dataKey="value"
        name="Flux"
        domain={[minValue, maxValue]}
      >
        <Label value="Flux Density (mJy)" position="left" angle="-90" />
      </YAxis>
      <ZAxis type="number" dataKey="size" name="Size" range={[40, 600]} />
    </ScatterPlot>
  );
};

export default FluxPlot;
