import { Modal, Spinner } from "react-bootstrap";

const LoadingModal = () => (
  <Modal show={true} size="xl">
    <Modal.Body>
      <h4 className="text-primary">Data files</h4>
      <h5>
        <Spinner animation="border" variant="primary" />{" "}
        <span className="text-primary">Fetching files... </span>
      </h5>
    </Modal.Body>
  </Modal>
);

export default LoadingModal;
