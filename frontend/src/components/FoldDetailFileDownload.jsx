import { graphql, useLazyLoadQuery, usePreloadedQuery } from "react-relay";
import FileDownloadModal from "./FileDownloadModal";

export const foldDetailFileDownloadQuery = graphql`
  query FoldDetailFileDownloadQuery($mainProject: String!, $jname: String!) {
    filePulsarList(mainProject: $mainProject, jname: $jname) {
      edges {
        node {
          id
          path
          fileSize
        }
      }
    }
  }
`;

const FoldDetailFileDownload = ({ visible, setShow, queryRef }) => {
  const data = usePreloadedQuery(foldDetailFileDownloadQuery, queryRef);

  return (
    <FileDownloadModal
      visible={visible}
      data={data.filePulsarList}
      setShow={setShow}
    />
  );
};

export default FoldDetailFileDownload;
