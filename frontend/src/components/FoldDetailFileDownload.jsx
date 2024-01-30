import { graphql, useFragment } from "react-relay";
import FileDownloadModal from "./FileDownloadModal";

const FoldDetailFileDownloadQuery = graphql`
  fragment FoldDetailFileDownloadFragment on Query
  @argumentDefinitions(jname: { type: "String!" }) {
    filePulsarList(jname: $jname) {
      edges {
        node {
          path
          fileSize
        }
      }
    }
  }
`;

const FoldDetailFileDownload = ({ visible, data, setShow }) => {
  const fragmentData = useFragment(FoldDetailFileDownloadQuery, data);
  console.log("FoldDetailFileDownload fragmentData", fragmentData);

  return (
    <FileDownloadModal
      visible={visible}
      fragmentData={fragmentData.filePulsarList}
      setShow={setShow}
    />
  );
};

export default FoldDetailFileDownload;
