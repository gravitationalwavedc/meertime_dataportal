import { Modal, Spinner } from "react-bootstrap";

const LoadingModal = ({ heading, loadingMessage }) => (
  <Modal show={true} size="xl">
    <Modal.Body>
      <h4 className="text-primary">{heading}</h4>
      <h5>
        <Spinner animation="border" variant="primary" />{" "}
        <span className="text-primary">{loadingMessage}</span>
      </h5>
    </Modal.Body>
  </Modal>
);

export default LoadingModal;
