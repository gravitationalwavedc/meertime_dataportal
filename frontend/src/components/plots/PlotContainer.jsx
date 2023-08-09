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

  return (
    <Col md={10} className="pulsar-plot-display">
      <Form.Row>
        <Form.Group controlId="plotController" className="mb-0">
          <Form.Label>Plot Type</Form.Label>
          <Form.Control
            custom
            as="select"
            value={activePlot}
            onChange={(event) => setActivePlot(event.target.value)}
          >
            <option value="flux">Flux Density</option>
            <option value="snr">S/N</option>
            <option value="dm">DM</option>
            <option value="rm">RM</option>
          </Form.Control>
          <Form.Text className="text-muted">
            Drag to zoom, click empty area to reset, double click to view utc.
          </Form.Text>
        </Form.Group>
      </Form.Row>
      <div className="pulsar-plot-wrapper">
        { activePlot === "snr" ? (
          <SNRPlot maxPlotLength={maxPlotLength} {...rest} />
        ) : activePlot === "flux" ? (
          <FluxPlot maxPlotLength={maxPlotLength} {...rest} />
        ) : activePlot === "dm" ? (
          <DMPlot maxPlotLength={maxPlotLength} {...rest} />
        ) : activePlot === "rm" ? (
          <RMPlot maxPlotLength={maxPlotLength} {...rest} />
        // ) : activePlot === "residual" ? (
        //   <ResidualPlot maxPlotLength={maxPlotLength} {...rest} />
        ) : (
          <div>No known active plot</div>
        )}
      </div>
    </Col>
  );
};

export default PlotContainer;
