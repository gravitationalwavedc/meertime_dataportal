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
import {
  dmPlotData,
  formatYAxisTick,
  getXaxisFormatter,
  getXaxisLabel,
} from "./plotData";
import moment from "moment";

const DMPlot = ({ data, columns, search, maxPlotLength, xAxis }) => {
  const { plotData, minValue, maxValue, ticks } = dmPlotData(
    data,
    columns,
    search,
    maxPlotLength
  );
  console.log("DMPlot: minvalue = ", minValue);

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
        dataKey={xAxis}
        name={getXaxisLabel(xAxis)}
        domain={["auto", "auto"]}
        ticks={xAxis === "utc" ? ticks : undefined}
        tickFormatter={getXaxisFormatter(xAxis)}
      >
        <Label value={getXaxisLabel(xAxis)} position="bottom" />
      </XAxis>
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
      <Tooltip
        cursor={{ strokeDasharray: "3 3" }}
        formatter={toolTipFormatter}
      />
      <Legend
        align="right"
        verticalAlign="top"
        payload={[
          { id: "1", type: "square", value: "UHF", color: "#0d0887" },
          { id: "2", type: "circle", value: "L-Band", color: "#6001a6" },
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

export default DMPlot;
