import {
  CartesianGrid,
  Label,
  YAxis,
  ZAxis,
} from "recharts";
import React from "react";
import ScatterPlot from "./ScatterPlot";
import {
  dmPlotData,
  formatYAxisTick,
} from "./plotData";

const DMPlot = ({ data, columns, search, maxPlotLength, xAxis }) => {
  const { plotData, minValue, maxValue, ticks } = dmPlotData(
    data,
    columns,
    search,
    maxPlotLength
  );
  console.log("DMPlot: minvalue = ", minValue);

  return (
    <ScatterPlot data={plotData} xAxis={xAxis} ticks={ticks}>
      <CartesianGrid />
      <YAxis
        type="number"
        dataKey="value"
        name="DM"
        domain={["dataMin", "dataMax"]}
        tickFormatter={formatYAxisTick}
      >
        <Label value="Fit DM (pc cm^-3)" position="left" angle="-90" />
      </YAxis>
      <ZAxis type="number" dataKey="size" name="Size" range={[20, 300]} />
    </ScatterPlot>
  );
};

export default DMPlot;
