import { Button } from "react-bootstrap";
import { useLocation } from "found";
import EmptyStateMessage from "./EmptyStateMessage";
import { formatDDMonYYYY } from "../helpers";

const SingleObservationFileDownload = ({
  jname,
  utc,
  beam,
  mainProject,
  isAuthenticated,
  restricted = false,
  embargoEndDate = null,
  projectShort = "",
}) => {
  const location = useLocation();
  const currentPath = location.pathname;
  const loginPath = `/login/?next=${encodeURIComponent(currentPath)}`;

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

  const embargoBody = `You must be a member of ${
    projectShort || "this project"
  } to download this data until ${
    embargoEndDate ? formatDDMonYYYY(embargoEndDate) : "the embargo is lifted"
  }.`;

  return (
    <>
      {mainProject !== "MONSPSR" &&
        (!isAuthenticated ? (
          <EmptyStateMessage
            title="You must be logged in to download"
            body="Sign in to access full resolution, decimated, and ToA data."
            actionLabel="Log in"
            actionHref={loginPath}
          />
        ) : restricted ? (
          <EmptyStateMessage
            title="This observation is under embargo"
            body={embargoBody}
            variant="warning"
          />
        ) : (
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
        ))}
    </>
  );
};

export default SingleObservationFileDownload;
