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
import { rmPlotData } from "./plotData";
import moment from "moment";


const formatYAxisTick = (value) => {
  return value.toFixed(2);
};


const RMPlot = ({ data, columns, search, maxPlotLength }) => {
  const { plotData, minValue, maxValue } = rmPlotData(
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
    <ScatterPlot data={plotData}>
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
      <YAxis type="number" dataKey="value" name="RM" domain={[minValue, maxValue]} tickFormatter={formatYAxisTick}>
        <Label value="Fit RM (rad m^-2)" position="left" angle="-90" />
      </YAxis>
      <ZAxis type="number" dataKey="size" name="Size" range={[5, 100]} />
      <Tooltip
        cursor={{ strokeDasharray: "3 3" }}
        formatter={toolTipFormatter}
      />
      <Legend
        align="right"
        verticalAlign="top"
        payload={[
          { id: "1", type: "square",   value: "UHF",      color: "#0d0887" },
          { id: "2", type: "circle",   value: "L-Band",   color: "#6001a6" },
          { id: "3", type: "triangle", value: "S-Band_0", color: "#cd4a76" },
          { id: "4", type: "triangle", value: "S-Band_1", color: "#df6263" },
          { id: "5", type: "triangle", value: "S-Band_2", color: "#ee7b51" },
          { id: "6", type: "triangle", value: "S-Band_3", color: "#f9973f" },
          { id: "7", type: "triangle", value: "S-Band_4", color: "#fdb52e" },
        ]}
      />
    </ScatterPlot>
  );
};

export default RMPlot;
