import { commitMutation, createFragmentContainer, graphql } from "react-relay";
import { Button, Col } from "react-bootstrap";
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

export const performFileDownload = (e, path) => {
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

const DownloadFluxcalButtons = ({ data: { fileList } }) => (
  <>
    {fileList.edges.map(({ node }) => (
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

export default createFragmentContainer(DownloadFluxcalButtons, {
  data: graphql`
    fragment DownloadFluxcalButtons_data on Query
    @argumentDefinitions(
      jname: { type: "String!" }
      utc: { type: "String!" }
      project: { type: "String!" }
      band: { type: "Int!" }
      beam: { type: "Int!" }
    ) {
      fileList(
        jname: $jname
        utc: $utc
        project: $project
        band: $band
        beam: $beam
      ) {
        edges {
          node {
            path
            fileSize
          }
        }
      }
    }
  `,
});
