import React from 'react';
import { graphql, QueryRenderer } from 'react-relay';
import { Container, Row, Col } from 'react-bootstrap';
import environment from '../relayEnvironment';
import TopNav from '../components/TopNav';
import FoldTable from '../components/FoldTable';

const query = graphql`
  query FoldQuery {
    ...FoldTable_data
  }`;

const Fold = () => (
    <React.Fragment>
        <TopNav/>
        <Container fluid className="p-5">
            <Row>
                <Col>
                    <h4 className="mb-5">Fold Observations</h4>
                </Col>
            </Row>
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
