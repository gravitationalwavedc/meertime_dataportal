import { Button, Card, Col, Row } from "react-bootstrap";
import { Link } from "found";
import { meerWatchLink } from "../helpers";

const JobCard = ({ row, mainProject }) => (
  <Card className="mb-3 shadow-md job-card" data-testid="job-card">
    <Card.Body>
      <Card.Title>
        <span className="mr-3">{row.jname}</span> {row.project}
      </Card.Title>
      <Row>
        <Col md={3}>
          <p className="subtitle-1 text-primary-600 mb-2">Observations</p>
          <p>
            {row.numberOfObservations} in {row.timespan} days
          </p>
          <p className="overline mb-1">Last</p>
          <p>{row.latestObservation}</p>
          <p className="overline mb-1">First</p>
          <p>{row.firstObservation}</p>
        </Col>
        <Col md={3}>
          <p className="subtitle-1 text-primary-600 mb-2">Signal-to-noise</p>
          <p>{row.lastSnRaw} last raw</p>
          <p className="overline mb-1">Average (5 mins)</p>
          <p>{row.avgSnPipe ? row.avgSnPipe : "null"}</p>
          <p className="overline mb-1">Max (5 mins)</p>
          <p>{row.maxSnPipe ? row.maxSnPipe : "null"}</p>
        </Col>
        <Col md={3}>
          <p className="subtitle-1 text-primary-600 mb-2">Integration</p>
          <p>{row.totalIntegrationHours} hours total</p>
          <p className="overline mb-1">Last</p>
          <p>
            {row.lastIntegrationMinutes ? row.lastIntegrationMinutes : "null"}
          </p>
        </Col>
      </Row>
    </Card.Body>
    <Card.Footer>
      <Link
        to={`/fold/${row.projectKey}/${row.jname}/`}
        className="mr-2"
        size="sm"
        variant="link"
        as={Button}
      >
        View all observations
      </Link>
      <Link
        to={`/${mainProject}/${row.jname}/${row.latestObservation}/${row.latestObservationBeam}/`}
        className="mr-2"
        size="sm"
        variant="link"
        as={Button}
      >
        View last observation
      </Link>
      <Button size="sm" as="a" href={meerWatchLink(row.jname)} variant="link">
        View MeerWatch
      </Button>
    </Card.Footer>
  </Card>
);

export default JobCard;
