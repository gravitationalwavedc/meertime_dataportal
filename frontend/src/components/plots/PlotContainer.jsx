import { useState, Suspense } from "react";
import { Col } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import { graphql, useRefetchableFragment } from "react-relay";
import PlotlyPlot from "./PlotlyPlot";
import { getActivePlotData } from "./plotData";

const PlotContainerFragment = graphql`
  fragment PlotContainerFragment on Query
  @refetchable(queryName: "PlotContainerRefetchQuery")
  @argumentDefinitions(
    pulsar: { type: "String" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
    projectShort: { type: "String", defaultValue: "All" }
    minimumNsubs: { type: "Boolean", defaultValue: true }
    maximumNsubs: { type: "Boolean", defaultValue: false }
    obsNchan: { type: "Int", defaultValue: 1 }
    obsNpol: { type: "Int", defaultValue: 4 }
  ) {
    toa(
      pulsar: $pulsar
      mainProject: $mainProject
      projectShort: $projectShort
      minimumNsubs: $minimumNsubs
      maximumNsubs: $maximumNsubs
      obsNchan: $obsNchan
      obsNpol: $obsNpol
    ) {
      allProjects
      allNchans
      edges {
        node {
          observation {
            duration
            utcStart
            beam
            band
          }
          project {
            short
          }
          obsNchan
          minimumNsubs
          maximumNsubs
          dmCorrected
          id
          mjd
          dayOfYear
          binaryOrbitalPhase
          residualSec
          residualSecErr
          residualPhase
          residualPhaseErr
        }
      }
    }
  }
`;

const PlotContainer = ({
  tableData,
  toaData,
  urlQuery,
  jname,
  mainProject,
}) => {
  const [toaDataResult, refetch] = useRefetchableFragment(
    PlotContainerFragment,
    toaData
  );
  console.log("toaDataResult", toaDataResult);

  const timingProjects = toaDataResult.toa.allProjects;
  const allNchans = toaDataResult.toa.allNchans;

  const [xAxis, setXAxis] = useState("utc");
  const [activePlot, setActivePlot] = useState("Residual");
  const [timingProject, setTimingProject] = useState(urlQuery.timingProject || timingProjects[0]);
  const [obsNchan, setObsNchan] = useState(urlQuery.obsNchan || 1);
  const [maxNsub, setMaxNsub] = useState(urlQuery.maxNsub || false);
  const [obsNpol, setObsNpol] = useState(urlQuery.obsNpol || 4);

  const handleRefetch = ({
    newTimingProject = timingProject,
    newObsNchan = obsNchan,
    newMaxNsub = maxNsub,
    newObsNpol = obsNpol,
  } = {}) => {
    const url = new URL(window.location);
    url.searchParams.set("timingProject", newTimingProject);
    url.searchParams.set("obsNchan", newObsNchan);
    url.searchParams.set("maxNsub", newMaxNsub);
    url.searchParams.set("obsNpol", newObsNpol);
    window.history.pushState({}, "", url);
    const newMinimumNsubs = newMaxNsub === "false" ? true : false;
    const newMaximumNsubs = newMaxNsub === "true" ? true : false;
    console.log(
      "Refetching with:",
      newObsNchan,
      newMinimumNsubs,
      newMaximumNsubs,
      newObsNpol
    );
    refetch({
      projectShort: newTimingProject,
      obsNchan: newObsNchan,
      minimumNsubs: newMinimumNsubs,
      maximumNsubs: newMaximumNsubs,
      obsNpol: newObsNpol,
    });
  };

  const handleSetActivePlot = (activePlot) => {
    setActivePlot(activePlot);
  };

  const handleSetTimingProject = (newTimingProject) => {
    setTimingProject(newTimingProject);
    handleRefetch({
      newTimingProject: newTimingProject,
    });
  };

  const handleSetMaxNsub = (newMaxNsub) => {
    setMaxNsub(newMaxNsub);
    handleRefetch({
      newMaxNsub: newMaxNsub,
    });
  };

  const handleSetNchan = (newObsNchan) => {
    setObsNchan(parseInt(newObsNchan, 10));
    handleRefetch({
      newObsNchan: newObsNchan,
    });
  };

  const handleSetNpol = (newObsNpol) => {
    setObsNpol(parseInt(newObsNpol, 10));
    handleRefetch({
      newObsNpol: newObsNpol,
    });
  };

  console.log("timingProject", timingProject);
  const activePlotData = getActivePlotData(
    tableData,
    toaDataResult,
    activePlot,
    timingProject,
    jname,
    mainProject
  );
  console.log("activePlotData", activePlotData);

  return (
    <Suspense
      fallback={
        <div>
          <h3>Loading Plot...</h3>
        </div>
      }
    >
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
                value={obsNchan}
                onChange={(event) => handleSetNchan(event.target.value)}
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
                onChange={(event) => handleSetMaxNsub(event.target.value)}
              >
                <option value="true">True</option>
                <option value="false">False</option>
              </Form.Control>
            </Form.Group>
          )}
          {activePlot === "Residual" && (
            <Form.Group controlId="plotNpolController" className="col-md-2">
              <Form.Label>Npol</Form.Label>
              <Form.Control
                custom
                as="select"
                value={obsNpol}
                onChange={(event) => handleSetNpol(event.target.value)}
              >
                <option value="4">4</option>
                <option value="1">1</option>
              </Form.Control>
            </Form.Group>
          )}
        </Form.Row>
        <Form.Text className="text-muted">
          Drag a box to zoom, hover your mouse the top right and click Autoscale
          to zoom out, click on a point to view observation.
        </Form.Text>
        <div className="pulsar-plot-wrapper">
          <PlotlyPlot
            data={activePlotData}
            xAxis={xAxis}
            activePlot={activePlot}
          />
        </div>
      </Col>
    </Suspense>
  );
};

export default PlotContainer;
