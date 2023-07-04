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
import ZoomPlot from "./ZoomPlot";
import { fluxPlotData } from "./plotData";
import moment from "moment";

const FluxPlot = ({ data, columns, search, maxPlotLength }) => {
  const { lBandData, UHFData, ticks } = fluxPlotData(
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
    <ZoomPlot dataOne={lBandData} dataTwo={UHFData}>
      <CartesianGrid />
      <XAxis
        type="number"
        dataKey="time"
        name="UTC"
        domain={["auto", "auto"]}
        ticks={ticks}
        tickFormatter={(unixTime) => moment(unixTime).format("YYYY")}
      >
        <Label value="UTC" position="bottom" />
      </XAxis>
      <YAxis type="number" dataKey="value" name="Flux">
        <Label value="Flux Density" position="left" angle="-90" />
      </YAxis>
      <ZAxis type="number" dataKey="size" name="Size" range={[40, 600]} />
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
    </ZoomPlot>
  );
};

export default FluxPlot;
