import { Link } from "found";
import { useState, Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Col, Container, Row, Modal } from "react-bootstrap";
import { useScreenSize } from "../context/screenSize-context";
import Einstein from "../assets/images/einstein-coloured.png";
import GraphPattern from "../assets/images/graph-pattern.png";
import Footer from "../components/Footer";
import TopNav from "../components/TopNav";
import SingleObservationTable from "../components/SingleObservationTable";
import SingleObservationFileDownload from "../components/SingleObservationFileDownload";

const SingleObservationQuery = graphql`
  query SingleObservationQuery($pulsar: String!, $utc: String!, $beam: Int!) {
    ...SingleObservationTableFragment
      @arguments(pulsar: $pulsar, utc: $utc, beam: $beam)
  }
`;

const SingleObservationFileDownloadQuery = graphql`
  query SingleObservationFileDownloadQuery(
    $pulsar: String!
    $utc: String!
    $beam: Int!
  ) {
    ...SingleObservationFileDownloadFragment
      @arguments(jname: $pulsar, utc: $utc, beam: $beam)
  }
`;

const SingleObservation = ({
  // router,
  match: {
    params: { mainProject, jname, utc, beam },
  },
}) => {
  const { screenSize } = useScreenSize();
  const [downloadModalVisible, setDownloadModalVisible] = useState(false);
  const observationData = useLazyLoadQuery(SingleObservationQuery, {
    pulsar: jname,
    utc: utc,
    beam: beam,
  });
  const fileDownloadData = useLazyLoadQuery(
    SingleObservationFileDownloadQuery,
    {
      pulsar: jname,
      utc: utc,
      beam: beam,
    }
  );

  const title = (
    <Link size="sm" to={`/fold/${mainProject}/${jname}/`}>
      {jname}
    </Link>
  );

  return (
    <>
      <TopNav />
      <img src={GraphPattern} className="graph-pattern-top" alt="" />
      <Container>
        <Row>
          <Col>
            {screenSize === "xs" ? (
              <>
                <h4 className="text-primary-600">{title}</h4>
              </>
            ) : (
              <>
                <h2 className="text-primary-600">{title}</h2>
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
          <SingleObservationTable
            observationData={observationData}
            jname={jname}
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
            <SingleObservationFileDownload
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

export default SingleObservation;
