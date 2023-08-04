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
import { fluxPlotData } from "./plotData";
import moment from "moment";

const FluxPlot = ({ data, columns, search, maxPlotLength }) => {
  const { plotData, minValue, maxValue } = fluxPlotData(
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
        domain={["auto", "auto"]}
        ticks={ticks}
        tickFormatter={(unixTime) => moment(unixTime).format("YYYY")}
      >
        <Label value="UTC" position="bottom" />
      </XAxis>
      <YAxis type="number" dataKey="value" name="Flux" domain={[minValue, maxValue]}>
        <Label value="Flux Density (mJy)" position="left" angle="-90" />
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
          { id: "1", type: "circle", value: "L-Band", color: "#440154" },
          { id: "2", type: "square", value: "UHF", color: "#3e4a89" },
          { id: "3", type: "triangle", value: "S-Band_0", color: "#31688e" },
          { id: "4", type: "triangle", value: "S-Band_1", color: "#26828e" },
          { id: "5", type: "triangle", value: "S-Band_2", color: "#1f9e89" },
          { id: "6", type: "triangle", value: "S-Band_3", color: "#35b779" },
          { id: "7", type: "triangle", value: "S-Band_4", color: "#6ece58" },
        ]}
      />
    </ScatterPlot>
  );
};

export default FluxPlot;
