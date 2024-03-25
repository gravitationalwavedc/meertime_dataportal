import { graphql, useLazyLoadQuery } from "react-relay";
import FileDownloadModal from "./FileDownloadModal";
import { Suspense } from "react";

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

const FoldDetailFileDownload = ({ mainProject, jname, visible, setShow }) => {
  const data = useLazyLoadQuery(FoldDetailFileDownloadQuery, {
    mainProject: mainProject,
    jname: jname,
  });

  return (
    <Suspense fallback={<div>Loading...</div>}>
      <FileDownloadModal visible={visible} data={data} setShow={setShow} />
    </Suspense>
  );
};

export default FoldDetailFileDownload;
