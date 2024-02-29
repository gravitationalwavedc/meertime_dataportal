import { graphql, useFragment } from "react-relay";
import FileDownloadModal from "./FileDownloadModal";

const FoldDetailFileDownloadQuery = graphql`
  fragment FoldDetailFileDownloadFragment on Query
  @argumentDefinitions(
    mainProject: { type: "String!" }
    jname: { type: "String!" }
  ) {
    filePulsarList(
      mainProject: $mainProject
      jname: $jname
    ) {
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

  return (
    <FileDownloadModal
      visible={visible}
      fragmentData={fragmentData.filePulsarList}
      setShow={setShow}
    />
  );
};

export default FoldDetailFileDownload;
