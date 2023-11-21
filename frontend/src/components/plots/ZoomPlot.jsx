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
  filterBandData,
  formatYAxisTick,
  getXaxisFormatter,
  getXaxisLabel,
  getYaxisDomain,
  getYaxisLabel,
  getYaxisTicks,
  getZRange,
  toolTipFormatter,
} from "./plotData";
import _default from "react-bootstrap/esm/CardColumns";

const ZoomPlot = ({
  data,
  xAxis,
  activePlot,
  zoomArea,
  axisMin,
  axisMax,
  handleMouseDown,
  handleMouseMove,
  handleMouseUp,
  handleMouseLeave,
  handleScatterMouseLeave,
  handleScatterMouseEnter,
}) => {
  const { plotData, minValue, maxValue, medianValue, ticks } = filterBandData(
    data,
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
          onMouseLeave={handleMouseLeave}
        >
          <CartesianGrid />
          {plotData.map((dataBand, index) => (
            <Scatter
              name={dataBand.name}
              data={dataBand.data}
              fill={dataBand.colour}
              shape={dataBand.shape}
              onMouseUp={handleMouseUp}
              onMouseLeave={handleScatterMouseLeave}
              onMouseEnter={handleScatterMouseEnter}
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
            x1={axisMin.xMin ? axisMin.xMin : null}
            x2={axisMax.xMax ? axisMax.xMax : null}
            y1={axisMin.yMin ? axisMin.yMin : null}
            y2={axisMax.yMax ? axisMax.yMax : null}
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
            domain={getYaxisDomain(activePlot, minValue, maxValue)}
            ticks={getYaxisTicks(activePlot, minValue, maxValue, medianValue)}
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
