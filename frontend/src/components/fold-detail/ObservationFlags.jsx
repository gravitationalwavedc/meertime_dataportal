import { useState } from "react";
import { Col, Form } from "react-bootstrap";

const observationFilters = [
  {
    id: "timingJump",
    label: "Session Timing Jump",
    queryString: "Session Timing Jump",
    isActive: true,
    description:
      "Observed jump in ToA residuals of all observations of this session",
  },
  {
    id: "sensitivityReduction",
    label: "Session Sensitivity Reduction",
    queryString: "Session Sensitivity Reduction",
    isActive: false,
    description:
      "Reduced observed sensitivity, often by a factor of 16 due to incorrect antenna summation",
  },
  {
    id: "strongRFI",
    label: "Strong RFI",
    queryString: "Strong RFI",
    isActive: false,
    description: "Over 20% of RFI removed from observation",
  },
  {
    id: "rmDrift",
    label: "RM Drift",
    queryString: "RM Drift",
    isActive: true,
    description:
      "The Rotation Measure has drifted three weighted standard deviations from the weighted mean",
  },
  {
    id: "dmDrift",
    label: "DM Drift",
    queryString: "DM Drift",
    isActive: false,
    description:
      "The DM has drifted away from the median DM of the pulsar enough to cause a dispersion of three profile bins",
  },
  {
    id: "badOnlineFolding",
    label: "Bad Online Folding",
    queryString: "Bad online Folding",
    isActive: true,
    description:
      "The PTUSE online folding was drifting significantly due to an erroneous parameter file, causing the raw data to be irretrievably corrupted",
  },
];

const ObservationFlags = ({
  minimumSNR,
  setMinimumSNR,
  setExcludeBadges,
  excludeBadges,
}) => {
  const [localMinimumSNR, setLocalMinimumSNR] = useState(minimumSNR);

  const handleMinimumSNRSlide = (e) => {
    setLocalMinimumSNR(parseFloat(e.target.value));
  };

  const handleMinimumSNRToggle = (e) => {
    const minimumSNR = Number(e.target.value);
    const url = new URL(window.location);
    url.searchParams.set("minSNR", minimumSNR);
    window.history.pushState({}, "", url);
    setMinimumSNR(minimumSNR);
  };

  const handleCheckbox = (e) => {
    const flag = observationFilters.find((flag) => flag.id === e.target.id);

    let newExcludeBadges = [...excludeBadges];

    if (e.target.checked) {
      newExcludeBadges.push(flag.queryString);
    } else {
      newExcludeBadges = newExcludeBadges.filter((queryString) => {
        return queryString !== flag.queryString;
      });
    }

    setExcludeBadges(newExcludeBadges);
  };

  return (
    <Form className="mb-5">
      <Form.Row className="searchbar">
        <Col md={5} xl={4}>
          <h6 className="text-primary-600">Filter by Badge</h6>
          {observationFilters.map((checkBox) => (
            <Form.Check
              type="checkbox"
              key={checkBox.id}
              id={checkBox.id}
              className="mt-3"
            >
              <Form.Check.Input
                onChange={handleCheckbox}
                type="checkbox"
                defaultChecked={checkBox.isActive}
              />
              <Form.Check.Label>Hide {checkBox.label}</Form.Check.Label>
              <Form.Text muted>{checkBox.description}</Form.Text>
            </Form.Check>
          ))}
        </Col>
      </Form.Row>
      <Form.Row>
        <Col md={5} xl={4} className="mt-4">
          <Form.Label>
            Remove observations and ToAs with SNR less than {localMinimumSNR}
          </Form.Label>
          <Form.Control
            type="range"
            value={localMinimumSNR}
            min={0}
            max={50}
            onChange={handleMinimumSNRSlide}
            onMouseUp={handleMinimumSNRToggle}
            className="custom-slider"
          />
        </Col>
      </Form.Row>
    </Form>
  );
};

export default ObservationFlags;
