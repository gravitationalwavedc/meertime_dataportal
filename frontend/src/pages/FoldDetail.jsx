import { useState, Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Col, Container, Row, Modal } from "react-bootstrap";
import { useScreenSize } from "../context/screenSize-context";
import Einstein from "../assets/images/einstein-coloured.png";
import GraphPattern from "../assets/images/graph-pattern.png";
import Footer from "../components/Footer";
import TopNav from "../components/TopNav";
import FoldDetailTable from "../components/FoldDetailTable";
import FoldDetailFileDownload from "../components/FoldDetailFileDownload";
import TanTableTest from "../components/fold-detail-table/TanTableTest";

const FoldDetailQuery = graphql`
  query FoldDetailQuery($pulsar: String!, $mainProject: String) {
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
  const { screenSize } = useScreenSize();
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
  return (
    <>
      {/* <TopNav /> */}
      {/* <img src={GraphPattern} className="graph-pattern-top" alt="" /> */}
      {/* <Container> */}
      {/*   <Row> */}
      {/*     <Col> */}
      {/*       {screenSize === "xs" ? ( */}
      {/*         <> */}
      {/*           <h4 className="text-primary-600">{jname}</h4> */}
      {/*         </> */}
      {/*       ) : ( */}
      {/*         <> */}
      {/*           <h2 className="text-primary-600">{jname}</h2> */}
      {/*         </> */}
      {/*       )} */}
      {/*     </Col> */}
      {/*     <img src={Einstein} alt="" className="d-none d-md-block" /> */}
      {/*   </Row> */}
      <Suspense
        fallback={
          <div>
            <h3>Loading...</h3>
          </div>
        }
      >
        <TanTableTest tableData={tableData} />
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
      </Suspense>
      {/* </Container> */}
      {/* <Footer /> */}
    </>
  );
};

export default FoldDetail;
