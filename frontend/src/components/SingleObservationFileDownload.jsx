import { graphql, useFragment } from "react-relay";
import FileDownloadModal from "./FileDownloadModal";

const SingleObservationFileDownloadQuery = graphql`
  fragment SingleObservationFileDownloadFragment on Query
  @argumentDefinitions(
    mainProject: { type: "String!" }
    jname: { type: "String!" }
    utc: { type: "String!" }
    beam: { type: "Int!" }
  ) {
    fileSingleList(
      mainProject: $mainProject
      jname: $jname
      utc: $utc
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
`;

const SingleObservationFileDownload = ({ visible, data, setShow }) => {
  const fragmentData = useFragment(SingleObservationFileDownloadQuery, data);

  return (
    <FileDownloadModal
      visible={visible}
      data={fragmentData.fileSingleList}
      setShow={setShow}
    />
  );
};

export default SingleObservationFileDownload;
