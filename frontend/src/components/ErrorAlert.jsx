import { Alert, Button } from "react-bootstrap";

const ErrorAlert = ({ show, errors, onClose }) => {
  if (!show || !errors || errors.length === 0) return null;

  return (
    <Alert variant="danger" className="mb-4">
      {errors.map((error, index) => (
        <div key={index}>{error}</div>
      ))}
      <Button
        variant="outline-danger"
        size="sm"
        className="mt-2"
        onClick={onClose}
      >
        Close
      </Button>
    </Alert>
  );
};

export default ErrorAlert;
