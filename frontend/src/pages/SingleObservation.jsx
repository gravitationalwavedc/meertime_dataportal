import { Link } from "found";
import { useState, Suspense } from "react";
import { graphql, useLazyLoadQuery } from "react-relay";
import { Col, Container, Row } from "react-bootstrap";
import { useScreenSize } from "../context/screenSize-context";
import Einstein from "../assets/images/einstein-coloured.png";
import GraphPattern from "../assets/images/graph-pattern.png";
import Footer from "../components/Footer";
import TopNav from "../components/TopNav";
import SingleObservationTable from "../components/SingleObservationTable";

const SingleObservationQuery = graphql`
  query SingleObservationQuery($pulsar: String!, $utc: String!, $beam: Int!) {
    ...SingleObservationTableFragment
      @arguments(pulsar: $pulsar, utc: $utc, beam: $beam)
  }
`;

const SingleObservation = ({
  match: {
    params: { mainProject, jname, utc, beam },
  },
}) => {
  const { screenSize } = useScreenSize();

  // Convert beam from string to integer since URL params are always strings
  const beamInt = parseInt(beam, 10);

  const observationData = useLazyLoadQuery(SingleObservationQuery, {
    pulsar: jname,
    utc: utc,
    beam: beamInt,
  });

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
          />
        </Suspense>
      </Container>
      <Footer />
    </>
  );
};

export default SingleObservation;
