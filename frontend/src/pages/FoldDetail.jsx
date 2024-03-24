import { useState, Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Col, Container, Row, Modal } from "react-bootstrap";
import FoldDetailTable from "../components/FoldDetailTable";
import FoldDetailFileDownload from "../components/FoldDetailFileDownload";
import TanTableTest from "../components/fold-detail-table/TanTableTest";
import MainLayout from "../components/MainLayout";
import HeaderButtons from "../components/fold-detail-table/HeaderButtons";

const FoldDetailQuery = graphql`
  query FoldDetailQuery($pulsar: String!, $mainProject: String) {
    pulsarFoldResult(pulsar: $pulsar, mainProject: $mainProject) {
      description
    }

    ...FoldDetailTableFragment
      @arguments(pulsar: $pulsar, mainProject: $mainProject)

    ...TanTableTestFragment
      @arguments(pulsar: $pulsar, mainProject: $mainProject)
  }
`;

const PlotContainerQuery = graphql`
  query FoldDetailPlotContainerQuery(
    $pulsar: String!
    $mainProject: String
    $projectShort: String
    $minimumNsubs: Boolean
    $maximumNsubs: Boolean
    $obsNchan: Int
    $obsNpol: Int
  ) {
    ...PlotContainerFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        projectShort: $projectShort
        minimumNsubs: $minimumNsubs
        maximumNsubs: $maximumNsubs
        obsNchan: $obsNchan
        obsNpol: $obsNpol
      )
  }
`;

const FoldDetailFileDownloadQuery = graphql`
  query FoldDetailFileDownloadQuery($mainProject: String!, $pulsar: String!) {
    ...FoldDetailFileDownloadFragment
      @arguments(mainProject: $mainProject, jname: $pulsar)
  }
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject } = match.params;

  const [downloadModalVisible, setDownloadModalVisible] = useState(false);
  const tableData = useLazyLoadQuery(FoldDetailQuery, {
    pulsar: jname,
    mainProject: mainProject,
  });

  const toaData = useLazyLoadQuery(PlotContainerQuery, {
    pulsar: jname,
    mainProject: mainProject,
    projectShort: match.location.query.timingProject || "All",
    minimumNsubs: true,
    maximumNsubs: false,
    obsNchan: 1,
    obsNpol: 1,
  });

  const fileDownloadData = useLazyLoadQuery(FoldDetailFileDownloadQuery, {
    mainProject: mainProject,
    pulsar: jname,
  });

  console.log(tableData);

  return (
    <MainLayout
      title={jname}
      description={tableData.pulsarFoldResult.description}
    >
      <HeaderButtons
        mainProject={mainProject}
        jname={jname}
        tableData={tableData}
      />
      <TanTableTest
        tableData={tableData}
        mainProject={mainProject}
        jname={jname}
      />
      {/*     <FoldDetailTable */}
      {/*       query={FoldDetailQuery} */}
      {/*       tableData={tableData} */}
      {/*       toaData={toaData} */}
      {/*       jname={jname} */}
      {/*       mainProject={mainProject} */}
      {/*       match={match} */}
      {/*       setShow={setDownloadModalVisible} */}
      {/*     /> */}
      {/*   </Suspense> */}
      {/*   <Suspense */}
      {/*     fallback={ */}
      {/*       <Modal */}
      {/*         show={downloadModalVisible} */}
      {/*         onHide={() => setDownloadModalVisible(false)} */}
      {/*         size="xl" */}
      {/*       > */}
      {/*         <Modal.Body> */}
      {/*           <h4 className="text-primary">Loading</h4> */}
      {/*         </Modal.Body> */}
      {/*       </Modal> */}
      {/*     } */}
      {/*   > */}
      {/*     {localStorage.isStaff === "true" && ( */}
      {/*       <FoldDetailFileDownload */}
      {/*         visible={downloadModalVisible} */}
      {/*         data={fileDownloadData} */}
      {/*         setShow={setDownloadModalVisible} */}
      {/*       /> */}
      {/*     )} */}
    </MainLayout>
  );
};

export default FoldDetail;
