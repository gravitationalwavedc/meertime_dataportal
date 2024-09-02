import { useState } from "react";
import { Col, Row } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import { graphql, useRefetchableFragment } from "react-relay";
import PlotlyPlot from "./PlotlyPlot";
import { getActivePlotData } from "./plotData";
import { meertime, molonglo } from "../../telescopes";
import ObservationFlags from "../fold-detail/ObservationFlags";
import { useEffect } from "react";

const plotContainerFragment = graphql`
  fragment PlotContainerFragment on Query
  @refetchable(queryName: "PlotContainerRefetchQuery")
  @argumentDefinitions(
    pulsar: { type: "String" }
    mainProject: { type: "String", defaultValue: "MeerTIME" }
    projectShort: { type: "String", defaultValue: "All" }
    nsubType: { type: "String", defaultValue: "1" }
    obsNchan: { type: "Int", defaultValue: 1 }
    excludeBadges: { type: "[String]", defaultValue: [] }
    minimumSNR: { type: "Float", defaultValue: 8 }
  ) {
    toa(
      pulsar: $pulsar
      mainProject: $mainProject
      projectShort: $projectShort
      nsubType: $nsubType
      obsNchan: $obsNchan
      excludeBadges: $excludeBadges
      minimumSNR: $minimumSNR
    ) {
      allNchans
      allProjects
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
  queryData,
  jname,
  mainProject,
  match,
  minimumSNR,
  setMinimumSNR,
  excludeBadges,
  setExcludeBadges,
}) => {
  const [data, refetch] = useRefetchableFragment(
    plotContainerFragment,
    queryData
  );

  const { query } = match.location;

  console.log("Here", data);
  const allNchans = data.toa?.allNchans?.slice().sort((a, b) => a - b);

  const timingProjects =
    data.toa.allProjects.length === 0 ? ["All"] : data.toa.allProjects;

  const [xAxis, setXAxis] = useState("utc");
  const [activePlot, setActivePlot] = useState("Timing Residuals");
  const [projectShort, setProjectShort] = useState(
    query.timingProject || timingProjects[0]
  );
  const [obsNchan, setObsNchan] = useState(query.obsNchan || 1);
  const [nsubType, setNsubType] = useState(query.nsubType || "1");

  useEffect(() => {
    const url = new URL(window.location);
    url.searchParams.set("timingProject", projectShort);
    url.searchParams.set("obsNchan", obsNchan);
    url.searchParams.set("nsubType", nsubType);
    window.history.pushState({}, "", url);

    refetch({
      projectShort: projectShort,
      obsNchan: obsNchan,
      nsubType: nsubType,
      excludeBadges: excludeBadges,
      minimumSNR: minimumSNR,
    });
  }, [refetch, projectShort, obsNchan, nsubType, excludeBadges, minimumSNR]);

  const activePlotData = getActivePlotData(
    data,
    activePlot,
    projectShort,
    jname,
    mainProject
  );

  const plotTypes =
    mainProject === "MONSPSR" ? molonglo.plotTypes : meertime.plotTypes;

  return (
    <>
      <Row className="mt-5 mb-2">
        <Col>
          <h4 className="text-primary-600">Observation Plot</h4>
        </Col>
      </Row>
      <Row className="d-none d-sm-block">
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
                {plotTypes.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
          </Form.Row>
          <ObservationFlags
            minimumSNR={minimumSNR}
            setMinimumSNR={setMinimumSNR}
            data={queryData}
            setExcludeBadges={setExcludeBadges}
            excludeBadges={excludeBadges}
          />
          <Form.Row>
            <Form.Group
              controlId="xAxisController"
              className="col-md-2 searchbar"
            >
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
                  className="col-md-2 searchbar"
                >
                  <Form.Label>Timing Project</Form.Label>
                  <Form.Control
                    custom
                    as="select"
                    value={projectShort}
                    onChange={(event) => setProjectShort(event.target.value)}
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
                  className="col-md-2 searchbar"
                >
                  <Form.Label>Nchan</Form.Label>
                  <Form.Control
                    custom
                    as="select"
                    value={obsNchan}
                    onChange={(event) => setObsNchan(event.target.value)}
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
                  className="col-md-2 searchbar"
                >
                  <Form.Label>Nsub Type</Form.Label>
                  <Form.Control
                    custom
                    as="select"
                    value={nsubType}
                    onChange={(event) => setNsubType(event.target.value)}
                  >
                    <option value="1">1</option>
                    <option value="max">Max</option>
                    <option value="mode">Mode</option>
                  </Form.Control>
                </Form.Group>
              </>
            )}
          </Form.Row>
          <div className="pulsar-plot-wrapper">
            <PlotlyPlot
              data={activePlotData}
              xAxis={xAxis}
              activePlot={activePlot}
            />
          </div>
        </Col>
      </Row>
    </>
  );
};

export default PlotContainer;
