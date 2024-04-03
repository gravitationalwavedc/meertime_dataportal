import { Col, Row } from "react-bootstrap";
import { Form } from "react-bootstrap";
import ReactMarkdown from "react-markdown";

const ObservationFlags = ({
  observationBadges,
  handleObservationFlagToggle,
  totalBadgeExcludedObservations,
}) => {
  const badgeString =
    totalBadgeExcludedObservations +
    " observations removed by the above observation flags.";

  return (
    <>
      <Form.Row className="observationBadges">
        <Col md={4} xl={3}>
          {Object.keys(observationBadges).map((observationBadge, index) => (
            <Form.Check
              key={index}
              type="switch"
              id={observationBadge}
              label={observationBadge}
              checked={observationBadges[observationBadge]}
              onChange={() => handleObservationFlagToggle(observationBadge)}
            />
          ))}
        </Col>
      </Form.Row>
      <Row className="mb-3">
        <Col md={5}>
          <ReactMarkdown>{badgeString}</ReactMarkdown>
        </Col>
      </Row>
    </>
  );
};

export default ObservationFlags;
