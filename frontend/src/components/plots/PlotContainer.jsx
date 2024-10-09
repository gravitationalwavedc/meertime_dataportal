import { useState, Suspense } from "react";
import { Col, Row } from "react-bootstrap";
import Form from "react-bootstrap/Form";
import PlotlyPlot from "./PlotlyPlot";
import { meertime, molonglo } from "../../telescopes";
import ObservationFlags from "../fold-detail/ObservationFlags";
import PlotLoading from "./PlotLoading";

const PlotContainer = ({
  jname,
  mainProject,
  minimumSNR,
  setMinimumSNR,
  excludeBadges,
  setExcludeBadges,
  allProjects,
  mostCommonProject,
}) => {
  const [xAxis, setXAxis] = useState("utc");
  const [activePlot, setActivePlot] = useState("Timing Residuals");
  const [projectShort, setProjectShort] = useState(mostCommonProject);

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
            <Form.Group
              controlId="projectController"
              className="col-md-2 searchbar"
            >
              <Form.Label>Project</Form.Label>
              <Form.Control
                custom
                as="select"
                value={projectShort}
                onChange={(event) => setProjectShort(event.target.value)}
              >
                {allProjects.map((projectShort) => (
                  <option key={projectShort} value={projectShort}>
                    {projectShort}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
          </Form.Row>
          <div className="pulsar-plot-wrapper">
            <Suspense fallback={<PlotLoading />}>
              <PlotlyPlot
                xAxis={xAxis}
                activePlot={activePlot}
                jname={jname}
                mainProject={mainProject}
                projectShort={projectShort}
                excludeBadges={excludeBadges}
                minimumSNR={minimumSNR}
              />
            </Suspense>
          </div>
        </Col>
      </Row>
    </>
  );
};

export default PlotContainer;
