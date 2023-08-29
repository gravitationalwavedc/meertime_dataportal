import React, { useState } from "react";
import { Col } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import FluxPlot from "./FluxPlot";
import SNRPlot from "./SNRPlot";
import DMPlot from "./DMPlot";
import RMPlot from "./RMPlot";
import ResidualPlot from "./ResidualPlot";

const PlotContainer = ({ maxPlotLength, ...rest }) => {
  const [activePlot, setActivePlot] = useState("residual");
  const [xAxis, setXAxis] = useState("utc");

  return (
    <Col md={10} className="pulsar-plot-display">
      <Form.Row>
        <Form.Group controlId="plotController" className="col-md-2">
          <Form.Label>Plot Type</Form.Label>
          <Form.Control
            custom
            as="select"
            value={activePlot}
            onChange={(event) => setActivePlot(event.target.value)}
          >
            <option value="residual">Timing Residuals</option>
            <option value="flux">Flux Density</option>
            <option value="snr">S/N</option>
            <option value="dm">DM</option>
            <option value="rm">RM</option>
          </Form.Control>
        </Form.Group>
        { activePlot === "residual" &&
          // Only show the x-axis selector for the residual plot.
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
        }
      </Form.Row>
      <Form.Text className="text-muted">
        Drag to zoom, click empty area to reset, double click to view utc.
      </Form.Text>
      <div className="pulsar-plot-wrapper">
        { activePlot === "snr" ? (
          <SNRPlot maxPlotLength={maxPlotLength} {...rest} />
        ) : activePlot === "flux" ? (
          <FluxPlot maxPlotLength={maxPlotLength} {...rest} />
        ) : activePlot === "dm" ? (
          <DMPlot maxPlotLength={maxPlotLength} {...rest} />
        ) : activePlot === "rm" ? (
          <RMPlot maxPlotLength={maxPlotLength} {...rest} />
        ) : activePlot === "residual" ? (
          <ResidualPlot maxPlotLength={maxPlotLength} xAxis={xAxis} {...rest} />
        ) : (
          <div>No known active plot</div>
        )}
      </div>
    </Col>
  );
};

export default PlotContainer;
