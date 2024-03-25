import { useState, Suspense } from "react";
import { Col } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import { graphql, useRefetchableFragment } from "react-relay";
import PlotlyPlot from "./PlotlyPlot";
import { getActivePlotData } from "./plotData";
import { meertime, molonglo } from "../../telescopes";

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
    obsNpol: { type: "Int", defaultValue: 1 }
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
    pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
      edges {
        node {
          observation {
            id
            utcStart
            dayOfYear
            binaryOrbitalPhase
            duration
            beam
            bandwidth
            nchan
            band
            foldNbin
            nant
            nantEff
            restricted
            embargoEndDate
            project {
              short
            }
            ephemeris {
              dm
            }
            calibration {
              idInt
            }
          }
          pipelineRun {
            dm
            dmErr
            rm
            rmErr
            sn
            flux
          }
        }
      }
    }
  }
`;

const PlotContainer = ({ toaData, urlQuery, jname, mainProject }) => {
  const [toaDataResult, refetch] = useRefetchableFragment(
    PlotContainerFragment,
    toaData
  );
  const timingProjects = toaDataResult.toa.allProjects;
  const allNchans = toaDataResult.toa.allNchans.slice().sort((a, b) => a - b);

  const [xAxis, setXAxis] = useState("utc");
  const [activePlot, setActivePlot] = useState("Timing Residuals");
  const [timingProject, setTimingProject] = useState(
    urlQuery.timingProject || timingProjects[0]
  );
  const [obsNchan, setObsNchan] = useState(urlQuery.obsNchan || 1);
  const [maxNsub, setMaxNsub] = useState(urlQuery.maxNsub || false);
  const [obsNpol, setObsNpol] = useState(urlQuery.obsNpol || 1);

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
    const newMinimumNsubs = newMaxNsub === "false";
    const newMaximumNsubs = !newMinimumNsubs;
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

  const activePlotData = getActivePlotData(
    toaDataResult,
    activePlot,
    timingProject,
    jname,
    mainProject
  );

  const plotTypes =
    mainProject === "MONSPSR" ? molonglo.plotTypes : meertime.plotTypes;

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
              {plotTypes.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
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
          {activePlot === "Timing Residuals" && (
            <>
              <Form.Group
                controlId="plotProjectController"
                className="col-md-2"
              >
                <Form.Label>Timing Project</Form.Label>
                <Form.Control
                  custom
                  as="select"
                  value={timingProject}
                  onChange={(event) =>
                    handleSetTimingProject(event.target.value)
                  }
                >
                  {timingProjects.map((timingProject) => (
                    <option key={timingProject} value={timingProject}>
                      {timingProject}
                    </option>
                  ))}
                </Form.Control>
              </Form.Group>
              <Form.Group controlId="plotNchanController" className="col-md-2">
                <Form.Label>Nchan</Form.Label>
                <Form.Control
                  custom
                  as="select"
                  value={obsNchan}
                  onChange={(event) => handleSetNchan(event.target.value)}
                >
                  {allNchans.map((nchan) => (
                    <option key={nchan} value={nchan} disabled={nchan > 32}>
                      {nchan}
                    </option>
                  ))}
                </Form.Control>
              </Form.Group>
              <Form.Group
                controlId="plotMaxNsubController"
                className="col-md-2"
              >
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
              <Form.Group controlId="plotNpolController" className="col-md-2">
                <Form.Label>Npol</Form.Label>
                <Form.Control
                  custom
                  as="select"
                  value={obsNpol}
                  onChange={(event) => handleSetNpol(event.target.value)}
                >
                  <option value="1">1</option>
                  {mainProject !== "MONSPSR" && <option value="4">4</option>}
                </Form.Control>
              </Form.Group>
            </>
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
