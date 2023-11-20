import {
  CartesianGrid,
  Label,
  YAxis,
  ZAxis,
} from "recharts";
import React from "react";
import ScatterPlot from "./ScatterPlot";
import {
  rmPlotData,
  formatYAxisTick,
} from "./plotData";

const RMPlot = ({ data, columns, search, maxPlotLength, xAxis }) => {
  const { plotData, minValue, maxValue, ticks } = rmPlotData(
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
        name="RM"
        domain={[minValue, maxValue]}
        tickFormatter={formatYAxisTick}
      >
        <Label value="Fit RM (rad m^-2)" position="left" angle="-90" />
      </YAxis>
      <ZAxis type="number" dataKey="size" name="Size" range={[5, 100]} />
    </ScatterPlot>
  );
};

export default RMPlot;
