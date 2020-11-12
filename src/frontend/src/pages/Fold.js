import React from 'react';
import { graphql, QueryRenderer } from 'react-relay';
import { Container, Row, Col } from 'react-bootstrap';
import environment from '../relayEnvironment';
import TopNav from '../components/TopNav';
import FoldTable from '../components/FoldTable';
import GraphPattern from '../assets/images/graph-pattern.png';


const query = graphql`
  query FoldQuery {
    ...FoldTable_data
  }`;

const Fold = () => (
    <React.Fragment>
        <TopNav/>
        <Container>
            <Row>
                <Col>
                    <h4 className="mb-6 text-primary-600">Fold Observations</h4>
                </Col>
            </Row>
            <img src={GraphPattern} className="graph-pattern-top" alt=""/>
            <QueryRenderer
                environment={environment}
                query={query}
                fetchPolicy="store-and-network"
                render = {({ props }) => props ? <FoldTable data={props} /> : <h1>Loading...</h1>}
            />
        </Container>
    </React.Fragment>
);

export default Fold;
