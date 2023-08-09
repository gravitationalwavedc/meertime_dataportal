import {
  CartesianGrid,
  Label,
  Legend,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import React from "react";
import ScatterPlot from "./ScatterPlot";
import { dmPlotData } from "./plotData";
import moment from "moment";


const formatYAxisTick = (value) => {
  return value.toFixed(4);
};


const DMPlot = ({ data, columns, search, maxPlotLength }) => {
  const { lBandData, UHFData, minValue, maxValue } = dmPlotData(
    data,
    columns,
    search,
    maxPlotLength
  );

  const toolTipFormatter = (value, name) => {
    if (name === "UTC") {
      return [moment(value).format("DD-MM-YYYY-hh:mm:ss"), name];
    }

    if (name === "Size") {
      return [`${value} [m]`, "Integration time"];
    }

    return [value, name];
  };

  return (
    <ScatterPlot dataOne={lBandData} dataTwo={UHFData}>
      <CartesianGrid />
      <XAxis
        type="number"
        dataKey="time"
        name="UTC"
        tickCount={8}
        domain={["auto", "auto"]}
        tickFormatter={(unixTime) => moment(unixTime).format("DD/MM/YY")}
      >
        <Label value="UTC" position="bottom" />
      </XAxis>
      <YAxis type="number" dataKey="value" name="DM" domain={[minValue, maxValue]} tickFormatter={formatYAxisTick}>
        <Label value="Fit DM (pc cm^-3)" position="left" angle="-90" />
      </YAxis>
      <ZAxis type="number" dataKey="size" name="Size" range={[20, 300]} />
      <Tooltip
        cursor={{ strokeDasharray: "3 3" }}
        formatter={toolTipFormatter}
      />
      <Legend
        align="right"
        verticalAlign="top"
        payload={[
          { id: "1", type: "circle", value: "L-Band", color: "#8884d8" },
          { id: "1", type: "square", value: "UHF", color: "#e07761" },
        ]}
      />
    </ScatterPlot>
  );
};

export default DMPlot;
