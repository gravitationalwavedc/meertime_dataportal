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
    loadEphemerisQuery({ jname: jname, mainProject: mainProject });
    setEphemerisVisible(true);
  };

  const handleFileDownload = () => {
    loadFileDownloadQuery({ jname: jname, mainProject: mainProject });
    setFileDownloadVisible(true);
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
        <Suspense fallback={<LoadingModal />}>
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
};

export default HeaderButtons;
//
//   {tableData.pulsarFoldResult.ephemerisLink && (
//     <Button
//       size="sm"
//       className="mr-2 mb-2"
//       variant="outline-secondary"
//       onClick={() => createLink(tableData.pulsarFoldResult.ephemerisLink)}
//     >
//       Download ephemeris
//     </Button>
//   )}
//   {tableData.pulsarFoldResult.toasLink && (
//     <Button
//       size="sm"
//       className="mr-2 mb-2"
//       variant="outline-secondary"
//       disabled={!filesLoaded}
//       onClick={() => createLink(tableData.pulsarFoldResult.toasLink)}
//     >
//       {filesLoaded ? "Download TOAs" : "Loading TOAs"}
//     </Button>
//   )}
