import { commitMutation, graphql, useFragment } from "react-relay";
import { Button } from "react-bootstrap";
import environment from "../relayEnvironment";

const downloadFluxcalButtonsMutation = graphql`
  mutation DownloadFluxcalButtonsMutation(
    $input: FileDownloadTokenMutationInput!
  ) {
    getFileDownloadToken(input: $input) {
      downloadToken
    }
  }
`;

const generateDownload = (url) => {
  // Generate a file download link and click it to download the file
  const link = document.createElement("a");
  link.href = url;
  link.target = "_blank";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const performFileDownload = (e, path) => {
  e.preventDefault();
  const originalButtonLabel = e.target.innerText;
  e.target.classList.add("disabled");
  e.target.innerText = "Downloading...";

  commitMutation(environment, {
    mutation: downloadFluxcalButtonsMutation,
    variables: {
      input: {
        path: path,
      },
    },
    onCompleted: (response, errors) => {
      if (errors) {
        // eslint-disable-next-line no-alert
        alert("Unable to download file.");
        e.target.classList.remove("disabled");
      } else {
        generateDownload(
          import.meta.env.VITE_JOB_CONTROLLER_URL +
            response.getFileDownloadToken.downloadToken
        );

        setTimeout(() => {
          e.target.innerText = originalButtonLabel;
          e.target.classList.remove("disabled");
        }, 3000);
      }
    },
  });
};

const isChopped = (path) => {
  return path.includes(".ch.");
};

const downloadFluxcalButtonQuery = graphql`
  fragment DownloadFluxcalButtons_data on Query
  @argumentDefinitions(
    jname: { type: "String!" }
    utc: { type: "String!" }
    beam: { type: "Int!" }
  ) {
    fileList(jname: $jname, utc: $utc, beam: $beam) {
      edges {
        node {
          path
          fileSize
        }
      }
    }
  }
`;

const DownloadFluxcalButtons = ({ data }) => {
  const fragmentData = useFragment(downloadFluxcalButtonQuery, data);
  return (
    <>
      {fragmentData.fileList.edges?.map(({ node }) => (
        <Button
          key={node.path}
          size="sm"
          as="a"
          className="mr-2"
          variant="outline-secondary"
          onClick={(e) => performFileDownload(e, node.path)}
        >
          Download {isChopped(node.path) ? "Chopped" : ""} Fluxcal Archive
        </Button>
      ))}
    </>
  );
};

export default DownloadFluxcalButtons;
