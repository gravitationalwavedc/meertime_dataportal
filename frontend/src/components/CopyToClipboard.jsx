import React, { useState } from "react";
import { Button } from "react-bootstrap";

const CopyToClipboard = ({ textToCopy }) => {
  const [isCopied, setIsCopied] = useState(false);

  const handleCopyClick = () => {
    const textArea = document.createElement("textarea");
    textArea.value = textToCopy;

    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand("copy");
    document.body.removeChild(textArea);

    setIsCopied(true);

    // Reset the 'Copied' state after a brief delay
    setTimeout(() => {
      setIsCopied(false);
    }, 1500);
  };

  return (
    <div>
      <textarea className="form-control" rows="5" value={textToCopy} readOnly />
      <Button onClick={handleCopyClick}>
        {isCopied ? "Copied!" : "Copy to Clipboard"}
      </Button>
    </div>
  );
};

export default CopyToClipboard;
