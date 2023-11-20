import { graphql, useFragment } from "react-relay";
import FileDownloadModal from "./FileDownloadModal";

const SingleObservationFileDownloadQuery = graphql`
  fragment SingleObservationFileDownloadFragment on Query
  @argumentDefinitions(
    jname: { type: "String!" }
    utc: { type: "String!" }
    beam: { type: "Int!" }
  ) {
    fileSingleList(jname: $jname, utc: $utc, beam: $beam) {
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
  console.log("SingleObservationFileDownloadfragmentData", fragmentData);

  return (
    <FileDownloadModal
      visible={visible}
      fragmentData={fragmentData.fileSingleList}
      setShow={setShow}
    />
  );
};

export default SingleObservationFileDownload;
