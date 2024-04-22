import { Col, Row, Form, OverlayTrigger, Tooltip } from "react-bootstrap";
import { QuestionCircle } from "react-bootstrap-icons";
import ReactMarkdown from "react-markdown";

const ObservationFlags = ({
  observationBadges,
  handleObservationFlagToggle,
  totalBadgeExcludedObservations,
  badgeData,
}) => {
  const badgeString =
    totalBadgeExcludedObservations +
    " observations removed by the above observation flags.";

  const tooltip = (observationBadgeName) => {
    const observationBadge = badgeData.find(
      (obj) => obj.node.name === observationBadgeName
    );
    return <Tooltip id="tooltip">{observationBadge.node.description}</Tooltip>;
  };

  return (
    <>
      <Form.Row className="observationBadges">
        <Col md={4} xl={3}>
          {Object.keys(observationBadges).map((observationBadge, index) => (
            <Form.Check
              key={index}
              type="switch"
              id={observationBadge}
              label={
                <>
                  {observationBadge}
                  <OverlayTrigger
                    placement="right"
                    overlay={tooltip(observationBadge)}
                  >
                    <QuestionCircle style={{ cursor: "pointer" }} />
                  </OverlayTrigger>
                </>
              }
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
