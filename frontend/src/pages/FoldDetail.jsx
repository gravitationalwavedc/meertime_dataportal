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

const FoldDetailQuery = graphql`
  query FoldDetailQuery($pulsar: String!, $mainProject: String) {
    ...FoldDetailTableFragment
      @arguments(pulsar: $pulsar, mainProject: $mainProject)
  }
`;

const PlotContainerQuery = graphql`
  query FoldDetailPlotContainerQuery(
    $pulsar: String!
    $mainProject: String
    $minimumNsubs: Boolean
    $maximumNsubs: Boolean
    $obsNchan: Int
    $obsNpol: Int
  ) {
    ...PlotContainerFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        minimumNsubs: $minimumNsubs
        maximumNsubs: $maximumNsubs
        obsNchan: $obsNchan
        obsNpol: $obsNpol
      )
  }
`;

const FoldDetailFileDownloadQuery = graphql`
  query FoldDetailFileDownloadQuery($pulsar: String!) {
    ...FoldDetailFileDownloadFragment @arguments(jname: $pulsar)
  }
`;

const FoldDetail = ({ match }) => {
  const { jname, mainProject } = match.params;
  console.log("pulsar:", jname);
  console.log("mainProject:", mainProject);
  console.log("match:", match);
  const { screenSize } = useScreenSize();
  const [downloadModalVisible, setDownloadModalVisible] = useState(false);
  const tableData = useLazyLoadQuery(FoldDetailQuery, {
    pulsar: jname,
    mainProject: mainProject,
  });
  const toaData = useLazyLoadQuery(PlotContainerQuery, {
    pulsar: jname,
    mainProject: mainProject,
    minimumNsubs: true,
    maximumNsubs: false,
    obsNchan: 1,
    obsNpol: 4,
  });
  const fileDownloadData = useLazyLoadQuery(FoldDetailFileDownloadQuery, {
    pulsar: jname,
  });
  return (
    <>
      <TopNav />
      <img src={GraphPattern} className="graph-pattern-top" alt="" />
      <Container>
        <Row>
          <Col>
            {screenSize === "xs" ? (
              <>
                <h4 className="text-primary-600">{jname}</h4>
              </>
            ) : (
              <>
                <h2 className="text-primary-600">{jname}</h2>
              </>
            )}
          </Col>
          <img src={Einstein} alt="" className="d-none d-md-block" />
        </Row>
        <Suspense
          fallback={
            <div>
              <h3>Loading...</h3>
            </div>
          }
        >
          <FoldDetailTable
            query={FoldDetailQuery}
            tableData={tableData}
            toaData={toaData}
            jname={jname}
            mainProject={mainProject}
            match={match}
            setShow={setDownloadModalVisible}
          />
        </Suspense>
        <Suspense
          fallback={
            <Modal
              show={downloadModalVisible}
              onHide={() => setDownloadModalVisible(false)}
              size="xl"
            >
              <Modal.Body>
                <h4 className="text-primary">Loading</h4>
              </Modal.Body>
            </Modal>
          }
        >
          {localStorage.isStaff === "true" && (
            <FoldDetailFileDownload
              visible={downloadModalVisible}
              data={fileDownloadData}
              setShow={setDownloadModalVisible}
            />
          )}
        </Suspense>
      </Container>
      <Footer />
    </>
  );
};

export default FoldDetail;
