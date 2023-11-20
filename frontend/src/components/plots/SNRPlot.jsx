import {
  CartesianGrid,
  Label,
  YAxis,
  ZAxis,
} from "recharts";
import React from "react";
import ScatterPlot from "./ScatterPlot";
import { snrPlotData } from "./plotData";

const SNRPlot = ({ data, columns, search, maxPlotLength, xAxis }) => {
  console.log(data);
  const { plotData, minValue, maxValue, ticks } = snrPlotData(
    data,
    columns,
    search,
    maxPlotLength
  );

  return (
    <ScatterPlot data={plotData} xAxis={xAxis} ticks={ticks}>
      <CartesianGrid />
      <YAxis type="number" dataKey="value" name="S/N">
        <Label value="S/N" position="left" angle="-90" />
      </YAxis>
      <ZAxis
        type="number"
        dataKey="size"
        name="Size"
        domain={[minValue, maxValue]}
        range={[60, 400]}
      />
    </ScatterPlot>
  );
};

export default SNRPlot;
