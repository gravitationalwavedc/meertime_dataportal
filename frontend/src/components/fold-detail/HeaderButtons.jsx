import { useState, Suspense } from "react";
import { Button, Col, Row } from "react-bootstrap";
import Ephemeris, { ephemerisQuery } from "../Ephemeris";
import { createLink } from "../../helpers";
import { useQueryLoader } from "react-relay";
import FoldDetailFileDownload, {
  foldDetailFileDownloadQuery,
} from "../FoldDetailFileDownload";
import LoadingModal from "./LoadingModal";

const HeaderButtons = ({ jname, mainProject, toasLink }) => {
  const [ephemerisVisible, setEphemerisVisible] = useState(false);
  const [fileDownloadVisible, setFileDownloadVisible] = useState(false);

  const [ephemerisQueryRef, loadEphemerisQuery] =
    useQueryLoader(ephemerisQuery);

  const [fileDownloadQueryRef, loadFileDownloadQuery] = useQueryLoader(
    foldDetailFileDownloadQuery
  );

  const handleEphemerisButton = () => {
    setEphemerisVisible(true);
    loadEphemerisQuery({ jname: jname, mainProject: mainProject });
  };

  const handleFileDownload = () => {
    setFileDownloadVisible(true);
    loadFileDownloadQuery({ jname: jname, mainProject: mainProject });
  };

  if (localStorage.isStaff === "true") {
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
            onClick={handleFileDownload}
          >
            Download Data Files
          </Button>
          <Suspense
            fallback={
              <LoadingModal
                heading="Download Files"
                loadingMessage="Fetching data files"
              />
            }
          >
            {fileDownloadQueryRef !== null && (
              <FoldDetailFileDownload
                setShow={setFileDownloadVisible}
                visible={fileDownloadVisible}
                queryRef={fileDownloadQueryRef}
              />
            )}
          </Suspense>
          {toasLink && (
            <Button
              size="sm"
              className="mr-2 mb-2"
              variant="outline-secondary"
              onClick={() => createLink(toasLink)}
            >
              Download TOAs
            </Button>
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
          onClick={handleEphemerisButton}
        >
          View folding ephemeris
        </Button>
        <Suspense>
          {ephemerisQueryRef != null && (
            <Ephemeris
              show={ephemerisVisible}
              setShow={setEphemerisVisible}
              queryRef={ephemerisQueryRef}
            />
          )}
        </Suspense>
      </Col>
    </Row>
  );
};

export default HeaderButtons;
