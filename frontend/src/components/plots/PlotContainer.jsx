import React, { useState } from "react";
import { Col } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import PlotlyPlot from "./PlotlyPlot";
import { getActivePlotData } from "./plotData";

const PlotContainer = ({ data, timingProjects, allNchans }) => {
  const [xAxis, setXAxis] = useState("utc");
  const [activePlot, setActivePlot] = useState("Residual");
  const [timingProject, setTimingProject] = useState(timingProjects[0]);
  const [nchan, setNchan] = useState(1);
  const [maxNsub, setMaxNsub] = useState(false);

  const handleSetActivePlot = (activePlot) => {
    setActivePlot(activePlot);
  };

  const handleSetTimingProject = (timingProject) => {
    setTimingProject(timingProject);
  };

  const handleSetNchanProject = (nchan) => {
    setNchan(parseInt(nchan, 10));
  };

  const activePlotData = getActivePlotData(data, activePlot, timingProject, nchan, maxNsub);

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

        {activePlot === "Residual" && (
          <Form.Group controlId="plotProjectController" className="col-md-2">
            <Form.Label>Timing Project</Form.Label>
            <Form.Control
              custom
              as="select"
              value={timingProject}
              onChange={(event) => handleSetTimingProject(event.target.value)}
            >
              {timingProjects.map((timingProject, index) => (
                <option value={timingProject}>{timingProject}</option>
              ))}
            </Form.Control>
          </Form.Group>
        )}
        {activePlot === "Residual" && (
          <Form.Group controlId="plotNchanController" className="col-md-2">
            <Form.Label>Nchan</Form.Label>
            <Form.Control
              custom
              as="select"
              value={nchan}
              onChange={(event) => handleSetNchanProject(event.target.value)}
            >
              {allNchans.map((allNchan, index) => (
                <option value={allNchan}>{allNchan}</option>
              ))}
            </Form.Control>
          </Form.Group>
        )}
        {activePlot === "Residual" && (
          <Form.Group controlId="plotMaxNsubController" className="col-md-2">
            <Form.Label>Max Nsub</Form.Label>
            <Form.Control
              custom
              as="select"
              value={maxNsub}
              onChange={(event) => setMaxNsub(event.target.value)}
            >
              <option value="true">True</option>
              <option value="false">False</option>
            </Form.Control>
          </Form.Group>
        )}
      </Form.Row>
      <Form.Text className="text-muted">
        Drag a box to zoom, hover your mouse the top right and click Autoscale to zoom out, click on a point to view observation.
      </Form.Text>
      <div className="pulsar-plot-wrapper">
        <PlotlyPlot
          data={activePlotData}
          xAxis={xAxis}
          activePlot={activePlot}
        />
      </div>
    </Col>
  );
};

export default PlotContainer;
