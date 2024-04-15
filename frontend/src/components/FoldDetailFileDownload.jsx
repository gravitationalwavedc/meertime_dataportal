import { graphql, useLazyLoadQuery } from "react-relay";
import FileDownloadModal from "./FileDownloadModal";

const FoldDetailFileDownloadQuery = graphql`
  query FoldDetailFileDownloadQuery($mainProject: String!, $jname: String!) {
    filePulsarList(mainProject: $mainProject, jname: $jname) {
      edges {
        node {
          path
          fileSize
        }
      }
    }
  }
`;

const FoldDetailFileDownload = ({
  mainProject,
  jname,
  visible,
  setShow,
  setFilesLoaded,
}) => {
  const data = useLazyLoadQuery(FoldDetailFileDownloadQuery, {
    mainProject: mainProject,
    jname: jname,
  });

  setFilesLoaded(true);

  return (
    <FileDownloadModal
      visible={visible}
      data={data.filePulsarList}
      setShow={setShow}
    />
  );
};

export default FoldDetailFileDownload;
