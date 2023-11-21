import React from "react";
import {
  CartesianGrid,
  ErrorBar,
  Label,
  Legend,
  ReferenceArea,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  ZAxis,
} from "recharts";
import {
  formatYAxisTick,
  getActivePlotData,
  getXaxisFormatter,
  getXaxisLabel,
  getYaxisLabel,
  getZRange,
  toolTipFormatter,
} from "./plotData";
import _default from "react-bootstrap/esm/CardColumns";

const ZoomPlot = ({
  data,
  xAxis,
  activePlot,
  zoomArea,
  handleSymbolClick,
  handleMouseDown,
  handleMouseMove,
  handleMouseUp,
}) => {
  const { plotData, minValue, maxValue, ticks } = getActivePlotData(
    data,
    activePlot,
    zoomArea
  );

  return (
    <>
      <ResponsiveContainer>
        <ScatterChart
          margin={{
            top: 20,
            right: 40,
            bottom: 20,
            left: 20,
          }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
        >
          <CartesianGrid />
          {plotData.map((dataBand, index) => (
            <Scatter
              name={dataBand.name}
              data={dataBand.data}
              fill={dataBand.colour}
              shape={dataBand.shape}
              onMouseUp={handleSymbolClick}
            >
              <ErrorBar
                dataKey="error"
                width={5}
                strokeWidth={2}
                stroke={dataBand.colour}
                direction="y"
              />
            </Scatter>
          ))}
          <ReferenceArea
            xMin={zoomArea.xMin ? zoomArea.xMin : null}
            xMax={zoomArea.xMax ? zoomArea.xMax : null}
            yMin={zoomArea.yMin ? zoomArea.yMin : null}
            yMax={zoomArea.yMax ? zoomArea.yMax : null}
          />
          <Legend
            align="right"
            verticalAlign="top"
            payload={[
              { id: "1", type: "square", value: "UHF", color: "#0d0887" },
              { id: "2", type: "circle", value: "L-Band", color: "#6001a6" },
              {
                id: "3",
                type: "triangle",
                value: "S-Band_0",
                color: "#cd4a76",
              },
              {
                id: "4",
                type: "triangle",
                value: "S-Band_1",
                color: "#df6263",
              },
              {
                id: "5",
                type: "triangle",
                value: "S-Band_2",
                color: "#ee7b51",
              },
              {
                id: "6",
                type: "triangle",
                value: "S-Band_3",
                color: "#f9973f",
              },
              {
                id: "7",
                type: "triangle",
                value: "S-Band_4",
                color: "#fdb52e",
              },
            ]}
          />
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
          <Tooltip
            cursor={{ strokeDasharray: "3 3" }}
            formatter={toolTipFormatter}
          />
          <YAxis
            type="number"
            dataKey="value"
            name={activePlot}
            domain={[minValue, maxValue]}
            tickFormatter={formatYAxisTick}
          >
            <Label
              value={getYaxisLabel(activePlot)}
              position="left"
              angle="-90"
            />
          </YAxis>
          <ZAxis
            type="number"
            dataKey="size"
            name="Size"
            range={getZRange(activePlot)}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </>
  );
};

export default ZoomPlot;
