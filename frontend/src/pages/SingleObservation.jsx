import { Link } from "found";
import { Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Col, Container, Row } from "react-bootstrap";
import { useScreenSize } from "../context/screenSize-context";
import Einstein from "../assets/images/einstein-coloured.png";
import GraphPattern from "../assets/images/graph-pattern.png";
import Footer from "../components/Footer";
import TopNav from "../components/TopNav";
import SingleObservationTable from "../components/SingleObservationTable";
import {
  selectSingleObservationMainProject,
  singleObservationQueryVariables,
} from "../helpers";

const SingleObservationQuery = graphql`
  query SingleObservationQuery(
    $pulsar: String!
    $mainProject: String!
    $utc: String!
    $beam: Int!
  ) {
    pulsarFoldResult(
      pulsar: $pulsar
      mainProject: $mainProject
      utcStart: $utc
      beam: $beam
    ) {
      edges {
        node {
          observation {
            project {
              mainProject {
                name
              }
            }
          }
        }
      }
    }
    ...SingleObservationTableFragment
      @arguments(
        pulsar: $pulsar
        mainProject: $mainProject
        utc: $utc
        beam: $beam
      )
  }
`;

const SingleObservation = ({
  match: {
    params: { mainProject, jname, utc, beam },
  },
}) => {
  const { screenSize } = useScreenSize();

  const observationData = useLazyLoadQuery(
    SingleObservationQuery,
    singleObservationQueryVariables({ jname, mainProject, utc, beam })
  );
  const selectedMainProject = selectSingleObservationMainProject(
    observationData,
    mainProject
  );

  const title = (
    <Link size="sm" to={`/fold/${selectedMainProject}/${jname}/`}>
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
          />
        </Suspense>
      </Container>
      <Footer />
    </>
  );
};

export default SingleObservation;
