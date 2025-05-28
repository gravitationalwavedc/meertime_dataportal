import { Alert, Button } from "react-bootstrap";
import { useState } from "react";

const TokenSuccessAlert = ({ show, token, onClose }) => {
  const [isCopied, setIsCopied] = useState(false);

  if (!show) return null;

  const handleCopyClick = () => {
    navigator.clipboard.writeText(token).then(() => {
      setIsCopied(true);
      setTimeout(() => {
        setIsCopied(false);
      }, 1500);
    });
  };

  return (
    <Alert variant="success" className="mb-4">
      <h5>API Token Created Successfully</h5>
      <p>Copy this token now - you won't be able to see it again:</p>

      <div className="d-flex align-items-center mb-3">
        <code
          className="bg-light border rounded p-2 flex-grow-1"
          style={{ wordBreak: "break-all" }}
        >
          {token}
        </code>
        <Button
          variant="success"
          onClick={handleCopyClick}
          className="px-4 py-2 ml-3"
          style={{ minWidth: "80px" }}
        >
          {isCopied ? "✓ Copied!" : "📋 Copy"}
        </Button>
      </div>

      <Button
        variant="outline-success"
        size="sm"
        className="mt-2"
        onClick={onClose}
      >
        Close
      </Button>
    </Alert>
  );
};

export default TokenSuccessAlert;
