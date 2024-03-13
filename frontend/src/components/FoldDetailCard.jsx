import { Button, Card, Col, Row } from "react-bootstrap";
import { Link } from "found";

function formatNumber(value, decimals) {
  return value ? value.toFixed(decimals) : "null";
}

const FoldDetailCard = ({ row }) => (
  <Card className="mb-3 shadow-md job-card" data-testid="job-card">
    <Card.Body>
      <Card.Title>
        <span className="mr-3">{row.utc}</span> {row.proposalShort}
      </Card.Title>
      <Row>
        <Col md={3}>
          <p className="overline mb-1">Length</p>
          <p>{formatNumber(row.observation.duration, 2)} [s]</p>
          <p className="overline mb-1">Beam</p>
          <p>{row.observation.beam}</p>
          <p className="overline mb-1">Band Width</p>
          <p>{row.observation.bandwidth}</p>
        </Col>
        <Col md={3}>
          <p className="overline mb-1">Nchan</p>
          <p>{row.observation.nchan}</p>
          <p className="overline mb-1">Band</p>
          <p>{row.observation.band}</p>
          <p className="overline mb-1">Nbin</p>
          <p>{row.observation.foldNbin}</p>
        </Col>
        <Col md={3}>
          <p className="overline mb-1">Nant</p>
          <p>{row.observation.nant}</p>
          <p className="overline mb-1">Nant eff</p>
          <p>{row.observation.nantEff}</p>
          <p className="overline mb-1">S/N</p>
          <p>{formatNumber(row.pipelineRun.sn, 1)}</p>
        </Col>
        <Col md={3}>
          <p className="overline mb-1">DM Backend</p>
          <p>{formatNumber(row.observation.ephemeris.dm, 2)}</p>
          <p className="overline mb-1">DM Fit</p>
          <p>{formatNumber(row.pipelineRun.dm, 1)}</p>
          <p className="overline mb-1">RM</p>
          <p>{formatNumber(row.pipelineRun.rm, 1)}</p>
        </Col>
      </Row>
    </Card.Body>
    {row.embargo ? (
      <Card.Footer className="embargoed">{row.embargo}</Card.Footer>
    ) : (
      <Card.Footer>
        <Link
          to={`/${row.mainProject}/${row.jname}/${row.utc}/${row.beam}/`}
          className="mr-2"
          size="sm"
          variant="link"
          as={Button}
        >
          View Observation
        </Link>
      </Card.Footer>
    )}
  </Card>
);

export default FoldDetailCard;
