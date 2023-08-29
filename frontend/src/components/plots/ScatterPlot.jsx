import React, { useEffect, useState } from "react";
import {
  ReferenceArea,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  ErrorBar,
} from "recharts";
import { Button } from "react-bootstrap";
import { useRouter } from "found";
import _default from "react-bootstrap/esm/CardColumns";

const DEFAULT_ZOOM = { x1: null, y1: null, x2: null, y2: null };

const ScatterPlot = ({ data, children }) => {
  const [dataBands, setFilteredData] = useState(data);
  const [zoomArea, setZoomArea] = useState(DEFAULT_ZOOM);
  const [isZooming, setIsZooming] = useState(false);
  const [isDrag, setIsDrag] = useState(false);

  const { router } = useRouter();

  useEffect(() => {
    setFilteredData(data);
  }, data);

  const handleSymbolClick = (symbolData) => {
    if (!isDrag) {
      router.push(symbolData.link);
    }
  };

  const handleZoomOut = () => {
    setFilteredData(data);
    setZoomArea(DEFAULT_ZOOM);
  };

  const handleMouseDown = (e) => {
    setIsZooming(true);
    const { xValue, yValue } = e || {};
    setZoomArea({ x1: xValue, y1: yValue, x2: xValue, y2: yValue });
  };

  const handleMouseMove = (e) => {
    if (isZooming) {
      setIsDrag(true);
      setZoomArea((prev) => ({
        ...prev,
        x2: e ? e.xValue : null,
        y2: e ? e.yValue : null,
      }));
    }
  };

  const handleMouseUp = () => {
    if (isDrag && isZooming) {
      setIsZooming(false);
      setIsDrag(false);
      let { x1, y1, x2, y2 } = zoomArea;

      // ensure x1 <= x2 and y1 <= y2
      if (x1 > x2) [x1, x2] = [x2, x1];
      if (y1 > y2) [y1, y2] = [y2, y1];

      const DataInRange = data.map((dataBand, index) => ({
        ...dataBand,
        data: dataBand.data.filter(
          (dataPoint) =>
            dataPoint.value >= y1 &&
            dataPoint.value <= y2 &&
            ( (
              dataPoint.time >= x1 &&
              dataPoint.time <= x2
            ) || (
              dataPoint.utc >= x1 &&
              dataPoint.utc <= x2
            ) || (
              dataPoint.date >= x1 &&
              dataPoint.date <= x2
            ) || (
              dataPoint.phase >= x1 &&
              dataPoint.phase <= x2
            ) )

        )
      }));

      setFilteredData(DataInRange);
      setZoomArea(DEFAULT_ZOOM);
    }
  };

  return (
    <>
      <Button
        variant="outline-secondary"
        size="sm"
        className="zoom-btn"
        onClick={handleZoomOut}
      >
        Zoom out
      </Button>
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
          {children}
          {dataBands.map((dataBand, index) => (
            <Scatter
              name={dataBand.name}
              data={dataBand.data}
              fill={dataBand.colour}
              shape={dataBand.shape}
              onMouseUp={handleSymbolClick}
            >
              <ErrorBar dataKey="error" width={5} strokeWidth={2} stroke={dataBand.colour} direction="y" />
            </Scatter>
          ))}
          <ReferenceArea
            x1={zoomArea.x1 ? zoomArea.x1 : null}
            x2={zoomArea.x2 ? zoomArea.x2 : null}
            y1={zoomArea.y1 ? zoomArea.y1 : null}
            y2={zoomArea.y2 ? zoomArea.y2 : null}
          />
        </ScatterChart>
      </ResponsiveContainer>
    </>
  );
};

export default ScatterPlot;
