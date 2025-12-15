import { useState, Suspense } from "react";
import { Button, Col, Row } from "react-bootstrap";
import Ephemeris, { ephemerisQuery } from "../Ephemeris";
import { useQueryLoader } from "react-relay";
import LoadingModal from "./LoadingModal";

const HeaderButtons = ({ jname, mainProject }) => {
  const [ephemerisVisible, setEphemerisVisible] = useState(false);
  const [ephemerisQueryRef, loadEphemerisQuery] =
    useQueryLoader(ephemerisQuery);

  const handleEphemerisButton = () => {
    setEphemerisVisible(true);
    loadEphemerisQuery({ jname: jname, mainProject: mainProject });
  };

  const handleDownloadFiles = (fileType) => {
    const downloadUrl = `${
      import.meta.env.VITE_DJANGO_DOWNLOAD_URL
    }/${jname}/${fileType}`;
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.target = "_blank";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Row>
      <Col>
        <Button
          size="sm"
          variant="outline-secondary"
          className="mr-2 mb-2"
          onClick={handleEphemerisButton}
        >
          View folding ephemeris
        </Button>
        <Suspense
          fallback={
            <LoadingModal
              heading="Folding Ephemeris"
              loadingMessage="Loading ephemeris"
            />
          }
        >
          {ephemerisQueryRef !== null && (
            <Ephemeris
              show={ephemerisVisible}
              setShow={setEphemerisVisible}
              queryRef={ephemerisQueryRef}
            />
          )}
        </Suspense>
        <Button
          size="sm"
          className="mr-2 mb-2"
          variant="outline-secondary"
          onClick={() => handleDownloadFiles("full")}
        >
          Download Full Resolution Data
        </Button>
        <Button
          size="sm"
          className="mr-2 mb-2"
          variant="outline-secondary"
          onClick={() => handleDownloadFiles("decimated")}
        >
          Download Decimated Data
        </Button>
        <Button
          size="sm"
          className="mr-2 mb-2"
          variant="outline-secondary"
          onClick={() => handleDownloadFiles("toas")}
        >
          Download ToAs
        </Button>
      </Col>
    </Row>
  );
};

export default HeaderButtons;
