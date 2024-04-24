import { useState } from "react";
import { Col, Row, Form, OverlayTrigger, Tooltip } from "react-bootstrap";
import { HiQuestionMarkCircle } from "react-icons/hi";
import ReactMarkdown from "react-markdown";

const ObservationFlags = ({
  observationBadges,
  handleObservationFlagToggle,
  minimumSNR,
  handleMinimumSNRToggle,
  totalBadgeExcludedObservations,
  badgeData,
}) => {
  const [localMinimumSNR, setLocalMinimumSNR] = useState(minimumSNR);
  const handleMinimumSNRSlide = (e) => {
    setLocalMinimumSNR(parseInt(e.target.value));
  };

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
        <Col md={5} xl={4}>
          {Object.keys(observationBadges).map((observationBadge, index) => (
            <Form.Check
              key={index}
              type="switch"
              id={observationBadge}
              label={
                <>
                  Remove {observationBadge}
                  <OverlayTrigger
                    placement="right"
                    overlay={tooltip(observationBadge)}
                  >
                    <HiQuestionMarkCircle
                      style={{ cursor: "pointer", marginLeft: "0.5rem" }}
                    />
                  </OverlayTrigger>
                </>
              }
              checked={observationBadges[observationBadge]}
              onChange={() => handleObservationFlagToggle(observationBadge)}
            />
          ))}
        </Col>
      </Form.Row>
      <Form.Row className="mb-3">
        <Form.Label>
          Remove observations and ToAs with SNR less than {localMinimumSNR}
        </Form.Label>
        <Form.Control
          type="range"
          value={localMinimumSNR}
          min={0}
          max={20}
          onChange={handleMinimumSNRSlide}
          onMouseUp={handleMinimumSNRToggle}
          className="custom-slider"
        />
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
