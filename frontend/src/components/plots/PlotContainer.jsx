import { useState, Suspense } from "react";
import { Col, Row } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import { graphql, useRefetchableFragment } from "react-relay";
import PlotlyPlot from "./PlotlyPlot";
import { getActivePlotData } from "./plotData";
import { meertime, molonglo } from "../../telescopes";
import ReactMarkdown from "react-markdown";

const PlotContainerFragment = graphql`
  fragment PlotContainerFragment on Query
  @refetchable(queryName: "PlotContainerRefetchQuery")
  @argumentDefinitions(
    pulsar: { type: "String" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
    projectShort: { type: "String", defaultValue: "All" }
    nsubType: { type: "String", defaultValue: "min" }
    obsNchan: { type: "Int", defaultValue: 1 }
    obsNpol: { type: "Int", defaultValue: 1 }
    excludeBadges: { type: "[String]", defaultValue: [] }
    minimumSNR: { type: "Float", defaultValue: 8 }
  ) {
    toa(
      pulsar: $pulsar
      mainProject: $mainProject
      projectShort: $projectShort
      nsubType: $nsubType
      obsNchan: $obsNchan
      obsNpol: $obsNpol
      excludeBadges: $excludeBadges
      minimumSNR: $minimumSNR
    ) {
      allNchans
      totalBadgeExcludedToas
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
          id
          obsNchan
          dmCorrected
          mjd
          snr
          dayOfYear
          binaryOrbitalPhase
          residualSec
          residualSecErr
          residualPhase
          residualPhaseErr
        }
      }
    }
    pulsarFoldResult(
      pulsar: $pulsar
      mainProject: $mainProject
      excludeBadges: $excludeBadges
      minimumSNR: $minimumSNR
    ) {
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

const PlotContainer = ({
  toaData,
  jname,
  mainProject,
  timingProjects,
  projectShort,
  setProjectShort,
  obsNchan,
  setObsNchan,
  obsNpol,
  setObsNpol,
  nsubType,
  setNsubType,
}) => {
  const [toaDataResult, refetch] = useRefetchableFragment(
    PlotContainerFragment,
    toaData
  );
  const allNchans = toaDataResult.toa.allNchans.slice().sort((a, b) => a - b);

  const [xAxis, setXAxis] = useState("utc");
  const [activePlot, setActivePlot] = useState("Timing Residuals");

  const handleRefetch = ({
    newProjectShort = projectShort,
    newObsNchan = obsNchan,
    newNsubType = nsubType,
    newObsNpol = obsNpol,
  } = {}) => {
    const url = new URL(window.location);
    url.searchParams.set("timingProject", newProjectShort);
    url.searchParams.set("obsNchan", newObsNchan);
    url.searchParams.set("nsubType", newNsubType);
    url.searchParams.set("obsNpol", newObsNpol);
    window.history.pushState({}, "", url);

    refetch({
      projectShort: newProjectShort,
      obsNchan: newObsNchan,
      nsubType: newNsubType,
      obsNpol: newObsNpol,
    });
  };

  const handleSetActivePlot = (activePlot) => {
    setActivePlot(activePlot);
  };

  const handleSetTimingProject = (newTimingProject) => {
    setProjectShort(newTimingProject);
    handleRefetch({
      newTimingProject: newTimingProject,
    });
  };

  const handleSetNsubType = (newNsubType) => {
    setNsubType(newNsubType);
    handleRefetch({
      newNsubType: newNsubType,
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
    projectShort,
    jname,
    mainProject
  );

  const plotTypes =
    mainProject === "MONSPSR" ? molonglo.plotTypes : meertime.plotTypes;

  const totalBadgeExcludedObservations =
    toaDataResult.toa.totalBadgeExcludedToas;
  const badgeString =
    totalBadgeExcludedObservations +
    " ToAs removed by the above observation flags.";

  return (
    <Suspense fallback={<h3>Loading Plot...</h3>}>
      <Row className="d-none d-sm-block">
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
                    value={projectShort}
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
                <Form.Group
                  controlId="plotNchanController"
                  className="col-md-2"
                >
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
                  <Form.Label>Nsub Type</Form.Label>
                  <Form.Control
                    custom
                    as="select"
                    value={nsubType}
                    onChange={(event) => handleSetNsubType(event.target.value)}
                  >
                    <option value="1">1</option>
                    <option value="max">Max</option>
                    <option value="mode">Mode</option>
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
          {activePlot === "Timing Residuals" && (
            <Row className="mb-3">
              <Col md={5}>
                <ReactMarkdown>{badgeString}</ReactMarkdown>
              </Col>
            </Row>
          )}
          <Form.Text className="text-muted">
            Drag a box to zoom, hover your mouse the top right and click
            Autoscale to zoom out, click on a point to view observation.
          </Form.Text>
          <div className="pulsar-plot-wrapper">
            <PlotlyPlot
              data={activePlotData}
              xAxis={xAxis}
              activePlot={activePlot}
            />
          </div>
        </Col>
      </Row>
    </Suspense>
  );
};

export default PlotContainer;
