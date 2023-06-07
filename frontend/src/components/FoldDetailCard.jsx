import { Button, Card, Col, Row } from "react-bootstrap";
import Link from "found/Link";

const FoldDetailCard = ({ row }) => (
  <Card className="mb-3 shadow-md job-card" data-testid="job-card">
    <Card.Body>
      <Card.Title>
        <span className="mr-3">{row.utc}</span> {row.proposalShort}
      </Card.Title>
      <Row>
        <Col md={3}>
          <p className="overline mb-1">Length</p>
          <p>{row.length} minutes</p>
          <p className="overline mb-1">Beam</p>
          <p>{row.beam}</p>
          <p className="overline mb-1">BW</p>
          <p>{row.bw}</p>
        </Col>
        <Col md={3}>
          <p className="overline mb-1">Nchan</p>
          <p>{row.nchan}</p>
          <p className="overline mb-1">Band</p>
          <p>{row.band}</p>
          <p className="overline mb-1">Nbin</p>
          <p>{row.nbin}</p>
        </Col>
        <Col md={3}>
          <p className="overline mb-1">Nant</p>
          <p>{row.nant}</p>
          <p className="overline mb-1">Nant eff</p>
          <p>{row.nantEff}</p>
          <p className="overline mb-1">S/N backend</p>
          <p>{row.snBackend}</p>
          <p className="overline mb-1">S/N meerpipe</p>
          <p>{row.snMeerpipe ? row.snMeerpipe : "null"}</p>
        </Col>
        <Col md={3}>
          <p className="overline mb-1">DM fold</p>
          <p>{row.dmFold}</p>
          <p className="overline mb-1">DM meerpipe</p>
          <p>{row.dmMeerpipe ? row.dmMeerpipe : "null"}</p>
          <p className="overline mb-1">RM meerpipe</p>
          <p>{row.rmMeerpipe ? row.rmMeerpipe : "null"}</p>
        </Col>
      </Row>
    </Card.Body>
    {!row.embargo ? (
      <Card.Footer>
        <Link
          to={`/${row.jname}/${row.utc}/${row.beam}/`}
          className="mr-2"
          size="sm"
          variant="link"
          as={Button}
        >
          View Observation
        </Link>
      </Card.Footer>
    ) : (
      <Card.Footer className="embargoed">{row.embargo}</Card.Footer>
    )}
  </Card>
);

export default FoldDetailCard;
