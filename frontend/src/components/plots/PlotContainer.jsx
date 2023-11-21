import React, { useState } from "react";
import { Col, Button } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import { useRouter } from "found";
import ZoomPlot from "./ZoomPlot";
import { getActivePlotData } from "./plotData";

const DEFAULT_ZOOM = { xMin: null, xMax: null, yMin: null, yMax: null };

const PlotContainer = (data) => {
  const [activePlot, setActivePlot] = useState("Residual");
  const [xAxis, setXAxis] = useState("utc");
  const [zoomArea, setZoomArea] = useState(DEFAULT_ZOOM);
  const [isZooming, setIsZooming] = useState(false);
  const [isDrag, setIsDrag] = useState(false);
  const [axisMin, setAxisMin] = useState({ xMin: null, yMin: null });
  const [axisMax, setAxisMax] = useState({ xMax: null, yMax: null });
  const [overScatter, setOverScatter] = useState(false);

  const { router } = useRouter();

  const handleSetActivePlot = (activePlot) => {
    setActivePlot(activePlot);
    setZoomArea(DEFAULT_ZOOM);
  }

  const handleZoomOut = () => {
    setIsDrag(false);
    setIsZooming(false);
    setAxisMin({ xMin: null, yMin: null });
    setAxisMax({ xMax: null, yMax: null });
    setZoomArea(DEFAULT_ZOOM);
  };

  const handleMouseLeave = () => {
    console.log("handleMouseLeave");
    setAxisMax({ xMax: axisMin.xMin, yMax: axisMin.yMin });
  };

  const handleMouseDown = (e) => {
    if (!overScatter) {
      setIsZooming(true);
      const { xValue, yValue } = e || {};
      setAxisMin({ xMin: xValue, yMin: yValue });
    }
  };

  const handleMouseMove = (e) => {
    if (isZooming) {
      const { xValue, yValue } = e || {};
      setIsDrag(true);
      setAxisMax({ xMax: xValue, yMax: yValue });
    }
  };

  const handleMouseUp = (symbolData) => {
    if (isDrag && isZooming) {
      setIsZooming(false);
      setIsDrag(false);
      let { xMin, yMin } = axisMin;
      let { xMax, yMax } = axisMax;

      // ensure xMin <= xMax and yMin <= yMax
      if (xMin > xMax) [xMin, xMax] = [xMax, xMin];
      if (yMin > yMax) [yMin, yMax] = [yMax, yMin];

      const newZoomArea = { xMin, xMax, yMin, yMax };

      setZoomArea(newZoomArea);
    } else if (overScatter) {
      router.push(symbolData.link);
    }
  };

  const handleScatterMouseEnter = () => {
    setOverScatter(true);
  }

  const handleScatterMouseLeave = () => {
    setOverScatter(false);
  }

  const activePlotData = getActivePlotData(data.data, activePlot);

  return (
    <Col md={10} className="pulsar-plot-display">
      <Form.Row>
        <Form.Group controlId="plotController" className="col-md-2">
          <Form.Label>Plot Type</Form.Label>
          <Form.Control
            custom
            as="select"
            value={activePlot}
            onChange={(event) => handleSetActivePlot(event.target.value)}
          >
            <option value="Residual">Timing Residuals</option>
            <option value="Flux Density">Flux Density</option>
            <option value="S/N">S/N</option>
            <option value="DM">DM</option>
            <option value="RM">RM</option>
          </Form.Control>
        </Form.Group>
        <Form.Group controlId="xAxisController" className="col-md-2">
          <Form.Label>X Axis</Form.Label>
          <Form.Control
            custom
            as="select"
            value={xAxis}
            onChange={(event) => setXAxis(event.target.value)}
          >
            <option value="utc">UTC date</option>
            <option value="day">Day of the year</option>
            <option value="phase">Binary Phase</option>
          </Form.Control>
        </Form.Group>
        <div>
        <Button
          style={{height: '50%', margin: "25% 0 25% 0"}}
          variant="outline-secondary"
          size="sm"
          className="mb-2"
          onClick={handleZoomOut}
        >
          Zoom out
        </Button>
        </div>
      </Form.Row>
      <Form.Text className="text-muted">
        Drag to zoom, click empty area to reset, double click to view utc.
      </Form.Text>
      <div className="pulsar-plot-wrapper">
        <ZoomPlot
          data={activePlotData}
          xAxis={xAxis}
          activePlot={activePlot}
          zoomArea={zoomArea}
          axisMin={axisMin}
          axisMax={axisMax}
          handleMouseDown={handleMouseDown}
          handleMouseMove={handleMouseMove}
          handleMouseUp={handleMouseUp}
          handleMouseLeave={handleMouseLeave}
          handleScatterMouseLeave={handleScatterMouseLeave}
          handleScatterMouseEnter={handleScatterMouseEnter}
        />
      </div>
    </Col>
  );
};

export default PlotContainer;
