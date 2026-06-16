import { useState, Suspense } from "react";
import { Button, Col, Row } from "react-bootstrap";
import { useLocation } from "found";
import Ephemeris, { ephemerisQuery } from "../Ephemeris";
import Template, { templateQuery } from "../Template";
import { useQueryLoader } from "react-relay";
import EmptyStateMessage from "../EmptyStateMessage";
import LoadingModal from "./LoadingModal";

const HeaderButtons = ({ jname, mainProject, isAuthenticated }) => {
  const location = useLocation();
  const currentPath = location.pathname;
  const loginPath = `/login/?next=${encodeURIComponent(currentPath)}`;
  const [ephemerisVisible, setEphemerisVisible] = useState(false);
  const [ephemerisQueryRef, loadEphemerisQuery] =
    useQueryLoader(ephemerisQuery);
  const [templateVisible, setTemplateVisible] = useState(false);
  const [templateQueryRef, loadTemplateQuery] = useQueryLoader(templateQuery);

  const handleEphemerisButton = () => {
    setEphemerisVisible(true);
    loadEphemerisQuery(
      { jname: jname, mainProject: mainProject },
      { fetchPolicy: "network-only" }
    );
  };

  const handleTemplateButton = () => {
    setTemplateVisible(true);
    loadTemplateQuery(
      { jname: jname, mainProject: mainProject },
      { fetchPolicy: "network-only" }
    );
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
          variant="outline-secondary"
          className="mr-2 mb-2"
          onClick={handleTemplateButton}
        >
          Download template
        </Button>
        <Suspense
          fallback={
            <LoadingModal
              heading="Pulse Profile Template"
              loadingMessage="Loading template"
            />
          }
        >
          {templateQueryRef !== null && (
            <Template
              show={templateVisible}
              setShow={setTemplateVisible}
              queryRef={templateQueryRef}
            />
          )}
        </Suspense>
        {mainProject !== "MONSPSR" &&
          (isAuthenticated ? (
            <>
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
            </>
          ) : (
            <EmptyStateMessage
              title="You must be logged in to download"
              body="Sign in to access full resolution, decimated, and ToA data."
              actionLabel="Log in"
              actionHref={loginPath}
            />
          ))}
      </Col>
    </Row>
  );
};

export default HeaderButtons;
