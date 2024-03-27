import { useState } from "react";
import { Button, Col, Row } from "react-bootstrap";
import Ephemeris from "../Ephemeris";
import { createLink, meerWatchLink } from "../../helpers";

const HeaderButtons = ({
  mainProject,
  jname,
  tableData,
  setDownloadModalVisible,
  filesLoaded,
}) => {
  const [ephemerisVisible, setEphemerisVisible] = useState(false);

  const ephemeris = tableData.pulsarFoldResult.residualEphemeris?.ephemerisData;

  if (localStorage.isStaff !== "true") {
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
            {ephemeris === undefined
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
          {ephemeris && (
            <Ephemeris
              ephemeris={ephemeris}
              show={ephemerisVisible}
              setShow={setEphemerisVisible}
            />
          )}
        </Col>
      </Row>
    );
  }

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
          {ephemeris === undefined
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
        {tableData.pulsarFoldResult.ephemerisLink && (
          <Button
            size="sm"
            className="mr-2 mb-2"
            variant="outline-secondary"
            onClick={() => createLink(tableData.pulsarFoldResult.ephemerisLink)}
          >
            Download ephemeris
          </Button>
        )}
        {tableData.pulsarFoldResult.toasLink && (
          <Button
            size="sm"
            className="mr-2 mb-2"
            variant="outline-secondary"
            disabled={!filesLoaded}
            onClick={() => createLink(tableData.pulsarFoldResult.toasLink)}
          >
            {filesLoaded ? "Download TOAs" : "Loading TOAs"}
          </Button>
        )}
        {
          <Button
            size="sm"
            className="mr-2 mb-2"
            variant="outline-secondary"
            disabled={!filesLoaded}
            onClick={() => setDownloadModalVisible(true)}
          >
            {filesLoaded ? "Download Data Files" : "Loading Data Files"}
          </Button>
        }
      </Col>
      {ephemeris && (
        <Ephemeris
          ephemeris={ephemeris}
          show={ephemerisVisible}
          setShow={setEphemerisVisible}
        />
      )}
    </Row>
  );
};

export default HeaderButtons;
