import { Button, Modal } from "react-bootstrap";

const DeleteTokenModal = ({ show, onHide, token, onConfirm }) => {
  return (
    <Modal show={show} onHide={onHide}>
      <Modal.Header closeButton>
        <Modal.Title>Confirm Token Deletion</Modal.Title>
      </Modal.Header>
      <Modal.Body>
        Are you sure you want to delete the token "{token?.name}"?
        <br />
        <strong>This action cannot be undone.</strong>
      </Modal.Body>
      <Modal.Footer>
        <Button variant="secondary" onClick={onHide}>
          Cancel
        </Button>
        <Button variant="danger" onClick={() => onConfirm(token?.id)}>
          Delete Token
        </Button>
      </Modal.Footer>
    </Modal>
  );
};

export default DeleteTokenModal;
