import { Button } from "react-bootstrap";

const SingleObservationFileDownload = ({ jname, utc, beam }) => {
  const downloadFile = (e, fileType) => {
    e.preventDefault();
    const downloadUrl = `${
      import.meta.env.VITE_DJANGO_DOWNLOAD_URL
    }/${jname}/${utc}/${beam}/${fileType}`;
    const link = document.createElement("a");
    link.href = downloadUrl;
    link.target = "_blank";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <>
      <Button
        size="sm"
        variant="outline-secondary"
        onClick={(e) => downloadFile(e, "full")}
        className="mr-2 mb-2"
      >
        Download Full Resolution
      </Button>
      <Button
        size="sm"
        variant="outline-secondary"
        onClick={(e) => downloadFile(e, "decimated")}
        className="mr-2 mb-2"
      >
        Download Decimated
      </Button>
      <Button
        size="sm"
        variant="outline-secondary"
        onClick={(e) => downloadFile(e, "toas")}
        className="mr-2 mb-2"
      >
        Download ToAs
      </Button>
    </>
  );
};

export default SingleObservationFileDownload;
