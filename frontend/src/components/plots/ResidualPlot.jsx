import {
  CartesianGrid,
  Label,
  YAxis,
  ZAxis,
} from "recharts";
import React from "react";
import ScatterPlot from "./ScatterPlot";
import {
  residualPlotData,
  formatYAxisTick,
} from "./plotData";

const ResidualPlot = ({ data, columns, search, maxPlotLength, xAxis }) => {
  console.log("ResidualPlot: ", data);
  const { plotData, minValue, maxValue, ticks } = residualPlotData(
    data,
    columns,
    search,
    maxPlotLength
  );
  console.log("plotData: ", plotData);

  return (
    <ScatterPlot data={plotData} xAxis={xAxis} ticks={ticks}>
      <CartesianGrid />
      <YAxis
        type="number"
        dataKey="value"
        name="Residual"
        domain={[minValue, maxValue]}
        tickFormatter={formatYAxisTick}
      >
        <Label value="Residual (μs)" position="left" angle="-90" />
      </YAxis>
      <ZAxis type="number" dataKey="size" name="Size" range={[20, 300]} />
    </ScatterPlot>
  );
};

export default ResidualPlot;
