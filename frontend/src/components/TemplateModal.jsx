import { Modal } from "react-bootstrap";
import { formatUTC } from "../helpers";
import { useEffect, useState } from "react";
import { useAuth } from "../auth/AuthContext";

const TemplateModal = ({ show, setShow, data }) => {
  const { isAuthenticated } = useAuth();
  const [updated, setUpdated] = useState("");
  const projectShort = data?.pulsarFoldResult?.foldingTemplate?.project.short;
  const band = data?.pulsarFoldResult?.foldingTemplate?.band;
  const templateFile = data?.pulsarFoldResult?.foldingTemplate?.templateFile;
  const isEmbargoed = data?.pulsarFoldResult?.foldingTemplateIsEmbargoed;
  const existsButInaccessible =
    data?.pulsarFoldResult?.foldingTemplateExistsButInaccessible;

  useEffect(() => {
    const createdAt = data?.pulsarFoldResult?.foldingTemplate?.createdAt;
    if (createdAt !== undefined) {
      setUpdated(formatUTC(createdAt));
    }
  }, [setUpdated, data]);

  // Determine the access message based on embargo status
  const getAccessMessage = () => {
    if (isEmbargoed === true) {
      return "You have access to this embargoed template as a project member. It is the template used by MeerPipe's latest run.";
    }
    return "This is the latest publicly available template used by MeerPipe.";
  };

  if (data.pulsarFoldResult.foldingTemplate === null) {
    return (
      <Modal
        className="template-modal"
        size="lg"
        show={show}
        onHide={() => setShow(false)}
        aria-labelledby="template-data"
      >
        <Modal.Header style={{ borderBottom: "none" }} closeButton>
          <Modal.Title className="text-primary">
            MeerPipe Pulse Profile Template
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {!isAuthenticated ? (
            <h5>Please log in to download files.</h5>
          ) : existsButInaccessible ? (
            <>
              <h5>
                No non-embargoed MeerPipe pulse profile template available to
                you.
              </h5>
              <p>
                Please request to join the relevant project for access at{" "}
                <a
                  href="https://pulsars.org.au/projects/"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  https://pulsars.org.au/projects/
                </a>
                .
              </p>
            </>
          ) : (
            <h5>No MeerPipe pulse profile template available.</h5>
          )}
        </Modal.Body>
      </Modal>
    );
  }

  return (
    <Modal
      className="template-modal"
      size="lg"
      show={show}
      onHide={() => setShow(false)}
      aria-labelledby="template-data"
    >
      <Modal.Header style={{ borderBottom: "none" }} closeButton>
        <Modal.Title className="text-primary">
          MeerPipe Pulse Profile Template
          <h6 className="text-muted">
            Created at {updated} from project {projectShort} ({band}).
          </h6>
          <h6 className="text-muted">{getAccessMessage()}</h6>
        </Modal.Title>
      </Modal.Header>
      <Modal.Body>
        <p>
          <a
            href={templateFile}
            target="_blank"
            rel="noopener noreferrer"
            download
          >
            Download Template File
          </a>
        </p>
      </Modal.Body>
    </Modal>
  );
};

export default TemplateModal;
