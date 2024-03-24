import { Col, Row, Button } from "react-bootstrap";
import Ephemeris from "../Ephemeris";
import { createLink, meerWatchLink } from "../../helpers";

const HeaderButtons = ({
  ephemeris,
  pulsarFoldResult,
  setEphemerisVisible,
  mainProject,
  jname,
  ephemerisUpdated,
  ephemerisVisible,
}) => {
  return (
    <Row>
      <Col>
        <Button
          size="sm"
          variant="outline-secondary"
          className="mr-2 mb-2"
          disabled={!ephemeris}
          onClick={() => setEphemerisVisible(true)}
        >
          {ephemeris === null
            ? "Folding ephemeris unavailable"
            : "View folding ephemeris"}
        </Button>
        {mainProject !== "MONSPSR" && (
          <Button
            size="sm"
            className="mr-2 mb-2"
            as="a"
            href={meerWatchLink(jname)}
            variant="outline-secondary"
          >
            View MeerWatch
          </Button>
        )}
        {localStorage.isStaff === "true" && pulsarFoldResult.ephemerisLink && (
          <Button
            size="sm"
            className="mr-2 mb-2"
            variant="outline-secondary"
            onClick={() => createLink(pulsarFoldResult.ephemerisLink)}
          >
            Download ephemeris
          </Button>
        )}
        {localStorage.isStaff === "true" && pulsarFoldResult.toasLink && (
          <Button
            size="sm"
            className="mr-2 mb-2"
            variant="outline-secondary"
            onClick={() => createLink(pulsarFoldResult.toasLink)}
          >
            Download TOAs
          </Button>
        )}
        {localStorage.isStaff === "true" && (
          <Button
            size="sm"
            className="mr-2 mb-2"
            variant="outline-secondary"
            onClick={() => setShow(true)}
          >
            Download data files
          </Button>
        )}
      </Col>
      {ephemeris && (
        <Ephemeris
          ephemeris={ephemeris}
          updated={ephemerisUpdated}
          show={ephemerisVisible}
          setShow={setEphemerisVisible}
        />
      )}
    </Row>
  );
};

export default HeaderButtons;
