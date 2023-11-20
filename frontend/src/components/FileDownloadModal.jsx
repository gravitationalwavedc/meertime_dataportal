import { Button, Modal, Table } from "react-bootstrap";
import { graphql, commitMutation } from "react-relay";
import environment from "../relayEnvironment";

const FileDownloadModalMutation = graphql`
  mutation FileDownloadModalMutation (
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
    mutation: FileDownloadModalMutation,
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

const FildDownloadModal = ({ visible, fragmentData, setShow }) => {
  // Work out file types and other info
  const files = fragmentData.edges.reduce((result, edge) => {
    const row = { ...edge.node };
    const pathArray = row.path.split("/");
    row.fileName = pathArray[pathArray.length - 1];

    const extensionArray = row.fileName.split(".");
    const fileExtension = extensionArray[extensionArray.length - 1];

    if ( row.fileName.includes("ch") && row.fileName.includes("t") && row.fileName.includes("p") ) {
      row.fileType = "Cleaned Decimated Archive";
    } else {
      row.fileType = "Cleaned Archive";
    }
    return [...result, { ...row }];
  }, []);
  const sortedFiles = files.sort((a, b) => b.fileName.localeCompare(a.fileName));
  console.log("files:", sortedFiles);
  return (
    <Modal show={visible} onHide={() => setShow(false)} size="xl">
      <Modal.Body>
        <h4 className="text-primary">Data files</h4>
        <Table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Type</th>
              <th>Size</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {sortedFiles.map((file) => (
              <tr key={file.path}>
                <td>{file.fileName} </td>
                <td>{file.fileType}</td>
                <td>{(file.fileSize / (1024 ** 2)).toFixed(2)} MB</td>
                <td>
                  <Button
                    size="sm"
                    variant="primary "
                    onClick={(e) => performFileDownload(e, file.path)}
                    disabled={file.fileSize === "0"}
                  >
                    Download
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </Modal.Body>
    </Modal>
  );
};

export default FildDownloadModal;
