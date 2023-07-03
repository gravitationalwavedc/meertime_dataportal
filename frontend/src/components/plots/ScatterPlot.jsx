import React, { useEffect, useState } from "react";
import {
  ReferenceArea,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
} from "recharts";
import { Button } from "react-bootstrap";
import { useRouter } from "found";

const DEFAULT_ZOOM = { x1: null, y1: null, x2: null, y2: null };

const ScatterPlot = ({ dataOne, dataTwo, children }) => {
  const [filteredDataOne, setFilteredDataOne] = useState(dataOne);
  const [filteredDataTwo, setFilteredDataTwo] = useState(dataTwo);
  const [zoomArea, setZoomArea] = useState(DEFAULT_ZOOM);
  const [isZooming, setIsZooming] = useState(false);
  const [isDrag, setIsDrag] = useState(false);

  const { router } = useRouter();

  useEffect(() => {
    setFilteredDataOne(dataOne);
    setFilteredDataTwo(dataTwo);
  }, [dataOne, dataTwo]);

  const handleSymbolClick = (symbolData) => {
    if (!isDrag) {
      router.push(symbolData.link);
    }
  };

  const handleZoomOut = () => {
    setFilteredDataOne(dataOne);
    setFilteredDataTwo(dataTwo);
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

      const DataOneInRange = filteredDataOne.filter(
        (dataPoint) =>
          dataPoint.time >= x1 &&
          dataPoint.time <= x2 &&
          dataPoint.value >= y1 &&
          dataPoint.value <= y2
      );
      const DataTwoInRange = filteredDataTwo.filter(
        (dataPoint) =>
          dataPoint.time >= x1 &&
          dataPoint.time <= x2 &&
          dataPoint.value >= y1 &&
          dataPoint.value <= y2
      );

      setFilteredDataOne(DataOneInRange);
      setFilteredDataTwo(DataTwoInRange);
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
          <Scatter
            name="L-Band"
            data={filteredDataOne}
            fill="#8884d8"
            shape="circle"
            onMouseUp={handleSymbolClick}
          />
          <Scatter
            name="UHF"
            data={filteredDataTwo}
            fill="#e07761"
            shape="square"
            onMouseUp={handleSymbolClick}
          />
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
